from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
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


class DocumentTypeModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "document_types"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    code: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    default_confidentiality: Mapped[str] = mapped_column(String(30), default="internal")
    allowed_mime_types: Mapped[list[str]] = mapped_column(JSONB, default=list)
    maximum_size_bytes: Mapped[int] = mapped_column(Integer, default=10_485_760)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class DocumentTemplateModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_templates"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    document_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_types.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class DocumentTemplateVersionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "document_template_versions"
    __table_args__ = (UniqueConstraint("template_id", "version_number"),)
    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_templates.id", ondelete="RESTRICT"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    based_on_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_template_versions.id", ondelete="RESTRICT")
    )
    storage_key: Mapped[str] = mapped_column(String(1000))
    content_sha256: Mapped[str] = mapped_column(String(64))
    variable_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id", ondelete="RESTRICT"))
    published_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DocumentRecordModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "document_records"
    __table_args__ = (
        Index("ix_document_records_business", "business_entity_type", "business_entity_id"),
        Index("ix_document_records_process", "process_instance_id", "status"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    document_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_types.id", ondelete="RESTRICT")
    )
    template_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_template_versions.id", ondelete="RESTRICT")
    )
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )
    business_entity_type: Mapped[str] = mapped_column(String(100))
    business_entity_id: Mapped[UUID]
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    registration_number: Mapped[str | None] = mapped_column(String(200))
    registration_date: Mapped[date | None] = mapped_column(Date)
    current_version_number: Mapped[int] = mapped_column(Integer, default=0)
    confidentiality_level: Mapped[str] = mapped_column(String(30), default="internal")
    created_by: Mapped[UUID] = mapped_column(ForeignKey("user_accounts.id", ondelete="RESTRICT"))


class DocumentVersionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number"),
        CheckConstraint("size_bytes >= 0", name="size_nonnegative"),
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(1000), unique=True)
    original_filename: Mapped[str] = mapped_column(String(500))
    safe_filename: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(200))
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    author_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    source_type: Mapped[str] = mapped_column(String(30))
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    immutable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DocumentChecklistItemModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "document_checklist_items"
    __table_args__ = (
        UniqueConstraint("business_entity_type", "business_entity_id", "document_type_id"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )
    business_entity_type: Mapped[str] = mapped_column(String(100))
    business_entity_id: Mapped[UUID]
    document_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_types.id", ondelete="RESTRICT")
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="missing")
    rejection_comment: Mapped[str | None] = mapped_column(Text)


class DocumentAcknowledgementModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "document_acknowledgements"
    __table_args__ = (UniqueConstraint("document_version_id", "assigned_employee_id"),)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )
    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="RESTRICT")
    )
    assigned_employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    evidence_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class DocumentSignatureModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "document_signatures"
    __table_args__ = (Index("ix_document_signatures_document", "document_id", "status"),)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )
    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="RESTRICT")
    )
    signer_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30), default="not_requested")
    provider_reference: Mapped[str | None] = mapped_column(String(500))
    manual_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
