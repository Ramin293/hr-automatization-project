"""Async persistence operations for timesheets and leave."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.errors import ResourceNotFoundError

from .models import (
    LeaveBalanceEntryModel,
    LeaveEntitlementModel,
    LeaveRequestModel,
    LeaveTypeModel,
    TimesheetEntryModel,
    TimesheetPeriodModel,
)

_LIVE_LEAVE_STATUSES = ("under_review", "under_approval", "awaiting_signature", "approved")
_MUTABLE_PERIOD_STATUSES = ("open", "under_review", "reopened")


class SqlAlchemyLeaveOperations:
    """Leave reads and balance arithmetic."""

    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def require_request_organization(self, request_id: UUID, organization_id: UUID) -> None:
        async with self._sessions() as session:
            actual = await session.scalar(
                select(LeaveRequestModel.organization_id).where(LeaveRequestModel.id == request_id)
            )
            if actual != organization_id:
                raise ResourceNotFoundError("leave request", request_id)

    async def get_request(self, request_id: UUID) -> LeaveRequestModel:
        async with self._sessions() as session:
            request = await session.get(LeaveRequestModel, request_id)
            if request is None:
                raise ResourceNotFoundError("leave request", request_id)
            return request

    async def list_requests(
        self,
        organization_id: UUID,
        offset: int,
        limit: int,
        employee_id: UUID | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[LeaveRequestModel], int]:
        async with self._sessions() as session:
            stmt = select(LeaveRequestModel).where(
                LeaveRequestModel.organization_id == organization_id
            )
            if employee_id is not None:
                stmt = stmt.where(LeaveRequestModel.employee_id == employee_id)
            if status is not None:
                stmt = stmt.where(LeaveRequestModel.status == status)

            total = await session.scalar(
                select(func.count()).select_from(stmt.subquery())
            )
            rows = await session.scalars(
                stmt.order_by(LeaveRequestModel.date_from.desc()).offset(offset).limit(limit)
            )
            return list(rows), int(total or 0)

    async def balance_days(
        self,
        employee_id: UUID,
        leave_type_id: UUID,
        as_of: date,
    ) -> Decimal:
        """Remaining days as the ledger sum over entitlements covering ``as_of``.

        The balance is never read from a stored counter: section 9 of the plan requires
        the remaining days to be reconstructible from the movements behind them.
        """

        async with self._sessions() as session:
            covering_entitlements = select(LeaveEntitlementModel.id).where(
                LeaveEntitlementModel.employee_id == employee_id,
                LeaveEntitlementModel.leave_type_id == leave_type_id,
                LeaveEntitlementModel.period_start <= as_of,
                LeaveEntitlementModel.period_end >= as_of,
            )
            total = await session.scalar(
                select(func.coalesce(func.sum(LeaveBalanceEntryModel.days), 0)).where(
                    LeaveBalanceEntryModel.employee_id == employee_id,
                    LeaveBalanceEntryModel.leave_type_id == leave_type_id,
                    LeaveBalanceEntryModel.entitlement_id.in_(covering_entitlements),
                )
            )
            return Decimal(total or 0)

    async def overlapping_requests(
        self,
        employee_id: UUID,
        date_from: date,
        date_to: date,
        exclude_request_id: UUID | None = None,
    ) -> Sequence[LeaveRequestModel]:
        """Live requests clashing with the given span.

        The database enforces this with a GiST exclusion constraint; this read exists so
        the caller can report the clash instead of surfacing an integrity error.
        """

        async with self._sessions() as session:
            stmt = select(LeaveRequestModel).where(
                LeaveRequestModel.employee_id == employee_id,
                LeaveRequestModel.status.in_(_LIVE_LEAVE_STATUSES),
                LeaveRequestModel.date_from <= date_to,
                LeaveRequestModel.date_to >= date_from,
            )
            if exclude_request_id is not None:
                stmt = stmt.where(LeaveRequestModel.id != exclude_request_id)
            return list(await session.scalars(stmt))

    async def active_leave_types(self, organization_id: UUID) -> Sequence[LeaveTypeModel]:
        async with self._sessions() as session:
            rows = await session.scalars(
                select(LeaveTypeModel)
                .where(
                    LeaveTypeModel.organization_id == organization_id,
                    LeaveTypeModel.active.is_(True),
                )
                .order_by(LeaveTypeModel.name)
            )
            return list(rows)


class SqlAlchemyTimesheetOperations:
    """Timesheet period and entry reads."""

    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def require_period_organization(self, period_id: UUID, organization_id: UUID) -> None:
        async with self._sessions() as session:
            actual = await session.scalar(
                select(TimesheetPeriodModel.organization_id).where(
                    TimesheetPeriodModel.id == period_id
                )
            )
            if actual != organization_id:
                raise ResourceNotFoundError("timesheet period", period_id)

    async def get_period(self, period_id: UUID) -> TimesheetPeriodModel:
        async with self._sessions() as session:
            period = await session.get(TimesheetPeriodModel, period_id)
            if period is None:
                raise ResourceNotFoundError("timesheet period", period_id)
            return period

    async def find_period(
        self,
        organization_unit_id: UUID,
        period_start: date,
    ) -> TimesheetPeriodModel | None:
        async with self._sessions() as session:
            return await session.scalar(
                select(TimesheetPeriodModel).where(
                    TimesheetPeriodModel.organization_unit_id == organization_unit_id,
                    TimesheetPeriodModel.period_start == period_start,
                )
            )

    async def period_accepts_edits(self, period_id: UUID) -> bool:
        """Whether rows may still be written directly.

        Once a period is closed or sent to accounting, section 8 requires changes to go
        through the correction process instead.
        """

        async with self._sessions() as session:
            status = await session.scalar(
                select(TimesheetPeriodModel.status).where(TimesheetPeriodModel.id == period_id)
            )
            if status is None:
                raise ResourceNotFoundError("timesheet period", period_id)
            return status in _MUTABLE_PERIOD_STATUSES

    async def list_entries(
        self,
        period_id: UUID,
        employee_id: UUID | None = None,
    ) -> Sequence[TimesheetEntryModel]:
        async with self._sessions() as session:
            stmt = select(TimesheetEntryModel).where(
                TimesheetEntryModel.timesheet_period_id == period_id
            )
            if employee_id is not None:
                stmt = stmt.where(TimesheetEntryModel.employee_id == employee_id)
            rows = await session.scalars(
                stmt.order_by(TimesheetEntryModel.employee_id, TimesheetEntryModel.entry_date)
            )
            return list(rows)

    async def hours_by_time_code(self, period_id: UUID, employee_id: UUID) -> dict[UUID, Decimal]:
        """Per-code hour totals: the shape accounting consumes once a period closes."""

        async with self._sessions() as session:
            rows = await session.execute(
                select(
                    TimesheetEntryModel.time_code_id,
                    func.coalesce(func.sum(TimesheetEntryModel.hours), 0),
                )
                .where(
                    TimesheetEntryModel.timesheet_period_id == period_id,
                    TimesheetEntryModel.employee_id == employee_id,
                )
                .group_by(TimesheetEntryModel.time_code_id)
            )
            return {code_id: Decimal(total) for code_id, total in rows.all()}
