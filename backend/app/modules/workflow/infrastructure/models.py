from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.database.mixins import RevisionMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessDefinitionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "process_definitions"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProcessDefinitionVersionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "process_definition_versions"
    __table_args__ = (
        UniqueConstraint("process_definition_id", "version_number"),
        CheckConstraint("version_number > 0", name="version_positive"),
        Index(
            "ix_process_definition_versions_effective",
            "process_definition_id",
            "status",
            "effective_from",
        ),
    )
    process_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definitions.id", ondelete="RESTRICT"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    based_on_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_definition_versions.id", ondelete="RESTRICT")
    )
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id", ondelete="RESTRICT"))
    published_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ActorRuleModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "workflow_actor_rules"
    __table_args__ = (UniqueConstraint("definition_version_id", "code"),)
    definition_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definition_versions.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    rule_type: Mapped[str] = mapped_column(String(50))
    configuration: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProcessStepDefinitionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "process_step_definitions"
    __table_args__ = (
        UniqueConstraint("definition_version_id", "code"),
        UniqueConstraint("definition_version_id", "stable_key"),
        CheckConstraint("sequence >= 0", name="sequence_nonnegative"),
        CheckConstraint("required_approvers > 0", name="required_approvers_positive"),
    )
    definition_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definition_versions.id", ondelete="CASCADE"), index=True
    )
    stable_key: Mapped[UUID]
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    step_type: Mapped[str] = mapped_column(String(50))
    sequence: Mapped[int] = mapped_column(Integer)
    actor_rule_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_actor_rules.id", ondelete="RESTRICT")
    )
    allowed_actions: Mapped[list[str]] = mapped_column(JSONB, default=list)
    due_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    required_document_type_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    completion_mode: Mapped[str] = mapped_column(String(10), default="all")
    required_approvers: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProcessTransitionDefinitionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "process_transition_definitions"
    __table_args__ = (
        UniqueConstraint("definition_version_id", "source_step_id", "target_step_id", "action"),
    )
    definition_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definition_versions.id", ondelete="CASCADE"), index=True
    )
    source_step_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_step_definitions.id", ondelete="CASCADE")
    )
    target_step_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_step_definitions.id", ondelete="CASCADE")
    )
    action: Mapped[str] = mapped_column(String(30))
    condition: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProcessInstanceModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "process_instances"
    __table_args__ = (
        Index("ix_process_instances_business", "business_type", "business_entity_id"),
        Index("ix_process_instances_scope_status", "organization_id", "status", "started_at"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    process_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definitions.id", ondelete="RESTRICT")
    )
    definition_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_definition_versions.id", ondelete="RESTRICT")
    )
    business_type: Mapped[str] = mapped_column(String(100))
    business_entity_id: Mapped[UUID]
    initiator_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    current_phase: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)


class WorkflowTaskModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "workflow_tasks"
    __table_args__ = (
        Index("ix_workflow_tasks_assigned", "assigned_user_id", "status", "due_at"),
        UniqueConstraint(
            "process_instance_id",
            "step_definition_id",
            "assigned_user_id",
            name="uq_workflow_task_assignment",
        ),
    )
    process_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_instances.id", ondelete="CASCADE"), index=True
    )
    step_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_step_definitions.id", ondelete="RESTRICT")
    )
    assigned_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT"), index=True
    )
    assigned_employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    assigned_unit_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision: Mapped[str | None] = mapped_column(String(30))
    decision_comment: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProcessHistoryEntryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "process_history_entries"
    __table_args__ = (
        Index("ix_process_history_instance_time", "process_instance_id", "occurred_at"),
    )
    process_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("process_instances.id", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(80))
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    summary: Mapped[str] = mapped_column(String(1000))
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FormDefinitionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "form_definitions"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class FormDefinitionVersionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "form_definition_versions"
    __table_args__ = (UniqueConstraint("form_definition_id", "version_number"),)
    form_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("form_definitions.id", ondelete="RESTRICT")
    )
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))
    based_on_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("form_definition_versions.id", ondelete="RESTRICT")
    )
    created_by: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id", ondelete="RESTRICT"))
    published_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FormFieldDefinitionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "form_field_definitions"
    __table_args__ = (UniqueConstraint("form_version_id", "code"),)
    form_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("form_definition_versions.id", ondelete="CASCADE")
    )
    code: Mapped[str] = mapped_column(String(100))
    label: Mapped[str] = mapped_column(String(300))
    field_type: Mapped[str] = mapped_column(String(50))
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_rules: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    reference_data_source: Mapped[str | None] = mapped_column(String(200))
    visibility_rule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    editability_rule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    confidentiality: Mapped[str] = mapped_column(String(30), default="internal")
    ordering: Mapped[int] = mapped_column(Integer)
    help_text: Mapped[str | None] = mapped_column(Text)


class FormSubmissionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "form_submissions"
    __table_args__ = (
        Index("ix_form_submissions_business", "business_entity_type", "business_entity_id"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    form_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("form_definition_versions.id", ondelete="RESTRICT")
    )
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )
    business_entity_type: Mapped[str] = mapped_column(String(100))
    business_entity_id: Mapped[UUID]
    submitted_by: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id", ondelete="RESTRICT"))
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
