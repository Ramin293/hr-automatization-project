from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.shared.api import CamelModel


class OrganizationRequest(CamelModel):
    organization_id: UUID


class CreateDefinitionRequest(OrganizationRequest):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)


class CreateDraftRequest(OrganizationRequest):
    name: str = Field(min_length=1, max_length=300)
    based_on_version_id: UUID | None = None


class ActorRuleRequest(OrganizationRequest):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=300)
    rule_type: str
    configuration: dict[str, Any] = Field(default_factory=dict)


class StepRequest(OrganizationRequest):
    stable_key: UUID | None = None
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=300)
    step_type: str
    sequence: int = Field(ge=0)
    actor_rule_id: UUID | None = None
    allowed_actions: list[str] = Field(min_length=1)
    due_duration_seconds: int | None = Field(default=None, gt=0)
    required_document_type_ids: list[UUID] = Field(default_factory=list)
    configuration: dict[str, Any] = Field(default_factory=dict)
    completion_mode: Literal["all", "any"] = "all"
    required_approvers: int = Field(default=1, gt=0)


class TransitionRequest(OrganizationRequest):
    source_step_id: UUID
    target_step_id: UUID
    action: str
    condition: dict[str, Any] | None = None
    priority: int = 0


class DecisionRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=2000)


class StartProcessRequest(OrganizationRequest):
    definition_code: str
    business_type: str
    business_entity_id: UUID
    context: dict[str, Any] = Field(default_factory=dict)


class TaskActionRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    action: Literal["submit", "approve", "return", "reject", "complete", "cancel", "reopen"]
    comment: str | None = Field(default=None, max_length=2000)
    idempotency_key: str = Field(min_length=8, max_length=200)


class ReassignTaskRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    assigned_user_id: UUID
    reason: str = Field(min_length=1, max_length=2000)


class FormDefinitionRequest(OrganizationRequest):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=300)


class FormDraftRequest(OrganizationRequest):
    based_on_version_id: UUID | None = None


class FormFieldRequest(OrganizationRequest):
    code: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=300)
    field_type: str
    required: bool = False
    validation_rules: dict[str, Any] = Field(default_factory=dict)
    reference_data_source: str | None = Field(default=None, max_length=200)
    visibility_rule: dict[str, Any] | None = None
    editability_rule: dict[str, Any] | None = None
    confidentiality: Literal["public", "internal", "confidential", "restricted"] = "internal"
    ordering: int = Field(ge=0)
    help_text: str | None = None


class FormPublishRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=2000)


class FormSubmissionRequest(OrganizationRequest):
    form_version_id: UUID
    process_instance_id: UUID | None = None
    business_entity_type: str = Field(min_length=1, max_length=100)
    business_entity_id: UUID
    data: dict[str, Any]
