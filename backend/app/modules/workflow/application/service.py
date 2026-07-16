from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from app.core.errors import ValidationError
from app.core.errors.codes import ErrorCode
from app.core.security.identity import Principal
from app.core.security.ports import AuthorizationPort
from app.modules.workflow.domain.entities import ConfigurationProblem

from .ports import WorkflowOperationsPort, WorkflowView


class WorkflowService:
    def __init__(
        self, operations: WorkflowOperationsPort, authorization: AuthorizationPort
    ) -> None:
        self._operations = operations
        self._authorization = authorization

    async def _require(
        self, principal: Principal, permission: str, organization_id: UUID | None = None
    ) -> None:
        await self._authorization.require(
            principal=principal, permission_code=permission, organization_id=organization_id
        )

    async def list_definitions(
        self, principal: Principal, organization_id: UUID
    ) -> Sequence[WorkflowView]:
        await self._require(principal, "workflow.definition.read", organization_id)
        return await self._operations.list_definitions(organization_id)

    async def create_definition(
        self, principal: Principal, organization_id: UUID, data: Mapping[str, Any]
    ) -> WorkflowView:
        await self._require(principal, "workflow.definition.manage", organization_id)
        return await self._operations.create_definition(organization_id, principal.user_id, data)

    async def create_draft(
        self,
        principal: Principal,
        organization_id: UUID,
        definition_id: UUID,
        based_on_version_id: UUID | None,
        name: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.definition.manage", organization_id)
        await self._operations.require_organization("definition", definition_id, organization_id)
        if based_on_version_id is not None:
            await self._operations.require_organization(
                "version", based_on_version_id, organization_id
            )
        return await self._operations.create_draft(
            definition_id, principal.user_id, based_on_version_id, name
        )

    async def validate(
        self, principal: Principal, organization_id: UUID, version_id: UUID
    ) -> tuple[ConfigurationProblem, ...]:
        await self._require(principal, "workflow.definition.manage", organization_id)
        await self._operations.require_organization("version", version_id, organization_id)
        return await self._operations.validate_version(version_id, principal.user_id)

    async def submit_review(
        self,
        principal: Principal,
        organization_id: UUID,
        version_id: UUID,
        revision: int,
        reason: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.definition.review", organization_id)
        await self._operations.require_organization("version", version_id, organization_id)
        return await self._operations.submit_review(
            version_id, principal.user_id, revision, _reason(reason)
        )

    async def return_draft(
        self,
        principal: Principal,
        organization_id: UUID,
        version_id: UUID,
        revision: int,
        reason: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.definition.review", organization_id)
        await self._operations.require_organization("version", version_id, organization_id)
        return await self._operations.return_draft(
            version_id, principal.user_id, revision, _reason(reason)
        )

    async def publish(
        self,
        principal: Principal,
        organization_id: UUID,
        version_id: UUID,
        revision: int,
        reason: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.definition.publish", organization_id)
        await self._operations.require_organization("version", version_id, organization_id)
        return await self._operations.publish(
            version_id, principal.user_id, revision, _reason(reason)
        )

    async def start_instance(
        self, principal: Principal, organization_id: UUID, data: Mapping[str, Any]
    ) -> WorkflowView:
        await self._require(principal, "workflow.task.act", organization_id)
        return await self._operations.start_instance(organization_id, principal.user_id, data)

    async def act_task(
        self,
        principal: Principal,
        organization_id: UUID,
        task_id: UUID,
        revision: int,
        action: str,
        comment: str | None,
        idempotency_key: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.task.act", organization_id)
        await self._operations.require_organization("task", task_id, organization_id)
        if action in {"return", "reject", "cancel"}:
            comment = _reason(comment or "")
        return await self._operations.act_task(
            task_id, principal.user_id, revision, action, comment, idempotency_key
        )

    async def reassign_task(
        self,
        principal: Principal,
        organization_id: UUID,
        task_id: UUID,
        revision: int,
        assigned_user_id: UUID,
        reason: str,
    ) -> WorkflowView:
        await self._require(principal, "workflow.task.reassign", organization_id)
        await self._operations.require_organization("task", task_id, organization_id)
        return await self._operations.reassign_task(
            task_id, principal.user_id, revision, assigned_user_id, _reason(reason)
        )


def _reason(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValidationError(
            "A reason is required.", code=ErrorCode.PROCESS_RETURN_REASON_REQUIRED
        )
    return normalized
