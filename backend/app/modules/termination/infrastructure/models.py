from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.database.mixins import RevisionMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TerminationReasonModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "termination_reasons"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    legal_review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    employee_initiated: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class TerminationCaseModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "termination_cases"
    __table_args__ = (
        Index("ix_termination_cases_scope_status", "organization_id", "status", "effective_date"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT"), index=True
    )
    initiated_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    initiated_by_employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    reason_id: Mapped[UUID] = mapped_column(
        ForeignKey("termination_reasons.id", ondelete="RESTRICT")
    )
    legal_basis: Mapped[str] = mapped_column(Text)
    requested_date: Mapped[date] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), index=True)
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )
    order_document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )
    primary_assignment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employee_assignments.id", ondelete="RESTRICT")
    )
    secondary_assignment_plan: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    manager_notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)


class OffboardingTaskModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "offboarding_tasks"
    __table_args__ = (UniqueConstraint("termination_case_id", "task_type"),)
    termination_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("termination_cases.id", ondelete="CASCADE"), index=True
    )
    task_type: Mapped[str] = mapped_column(String(50))
    assigned_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    assigned_employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    assigned_unit_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30), default="pending")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    restricted_notes: Mapped[str | None] = mapped_column(Text)


class OffboardingWaiverModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "offboarding_waivers"
    __table_args__ = (UniqueConstraint("offboarding_task_id"),)
    offboarding_task_id: Mapped[UUID] = mapped_column(
        ForeignKey("offboarding_tasks.id", ondelete="RESTRICT")
    )
    authorized_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
