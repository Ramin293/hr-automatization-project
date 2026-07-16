from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from app.core.errors import ValidationError
from app.core.security.identity import Principal
from app.core.security.ports import AuthorizationPort

from .ports import RecruitmentOperationsPort, RecruitmentView


class RecruitmentService:
    def __init__(
        self, operations: RecruitmentOperationsPort, authorization: AuthorizationPort
    ) -> None:
        self.operations = operations
        self.authorization = authorization

    async def require(
        self,
        principal: Principal,
        permission: str,
        organization_id: UUID,
        unit_id: UUID | None = None,
    ) -> None:
        await self.authorization.require(
            principal=principal,
            permission_code=permission,
            organization_id=organization_id,
            unit_id=unit_id,
        )

    async def create_request(
        self, principal: Principal, organization_id: UUID, unit_id: UUID, data: Mapping[str, object]
    ) -> RecruitmentView:
        await self.require(principal, "recruitment.request.create", organization_id, unit_id)
        return await self.operations.create_request(organization_id, principal.user_id, data)

    async def review_hr(
        self,
        principal: Principal,
        organization_id: UUID,
        request_id: UUID,
        revision: int,
        decision: str,
        comment: str,
    ) -> RecruitmentView:
        await self.require(principal, "recruitment.request.review_hr", organization_id)
        return await self.operations.review_request(
            request_id, principal.user_id, revision, decision, _reason(comment)
        )

    async def review_staffing(
        self,
        principal: Principal,
        organization_id: UUID,
        request_id: UUID,
        revision: int,
        decision: str,
        comment: str,
        staffing: Mapping[str, object],
    ) -> RecruitmentView:
        await self.require(principal, "recruitment.request.review_staffing", organization_id)
        return await self.operations.review_request(
            request_id, principal.user_id, revision, decision, _reason(comment), staffing
        )

    async def respond_offer(
        self,
        principal: Principal,
        organization_id: UUID,
        offer_id: UUID,
        revision: int,
        accepted: bool,
        reason: str | None,
    ) -> RecruitmentView:
        await self.require(principal, "recruitment.offer.manage", organization_id)
        if not accepted:
            reason = _reason(reason or "")
        return await self.operations.respond_offer(
            offer_id, principal.user_id, revision, accepted, reason
        )

    async def complete_hiring(
        self,
        principal: Principal,
        organization_id: UUID,
        case_id: UUID,
        revision: int,
        data: Mapping[str, object],
    ) -> RecruitmentView:
        await self.require(principal, "recruitment.hiring.manage", organization_id)
        return await self.operations.complete_hiring(case_id, principal.user_id, revision, data)


def _reason(value: str) -> str:
    result = value.strip()
    if not result:
        raise ValidationError("A reason is required.")
    return result
