from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from pydantic import Field

from app.shared.api import CamelModel


class OrganizationRequest(CamelModel):
    organization_id: UUID


class DocumentTypeRequest(OrganizationRequest):
    code: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)
    default_confidentiality: str = "internal"
    allowed_mime_types: list[str] = Field(default_factory=list)
    maximum_size_bytes: int = Field(default=10_485_760, gt=0)


class TemplateRequest(OrganizationRequest):
    document_type_id: UUID
    code: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=300)


class TemplateVersionRequest(OrganizationRequest):
    based_on_version_id: UUID | None = None
    storage_key: str = Field(min_length=1, max_length=1000)
    content_sha256: str = Field(min_length=64, max_length=64)
    variable_schema: dict[str, Any] = Field(default_factory=dict)


class PublishTemplateRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=2000)


class DocumentRecordRequest(OrganizationRequest):
    document_type_id: UUID
    template_version_id: UUID | None = None
    process_instance_id: UUID | None = None
    business_entity_type: str = Field(min_length=1, max_length=100)
    business_entity_id: UUID
    title: str = Field(min_length=1, max_length=500)
    confidentiality_level: str = "internal"


class RegisterDocumentRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    registration_number: str = Field(min_length=1, max_length=200)
    registration_date: date


class ManualSignatureRequest(OrganizationRequest):
    signer_user_id: UUID
    status: str = "signed"
    provider_reference: str | None = None
    evidence_metadata: dict[str, Any] = Field(default_factory=dict)


class ChecklistItemRequest(OrganizationRequest):
    process_instance_id: UUID | None = None
    business_entity_type: str
    business_entity_id: UUID
    document_type_id: UUID
    document_id: UUID | None = None
    mandatory: bool = True
    status: str = "missing"
    rejection_comment: str | None = None


class AcknowledgeRequest(OrganizationRequest):
    revision: int = Field(ge=1)
    evidence: dict[str, Any] = Field(default_factory=dict)


class GenerateDocumentRequest(OrganizationRequest):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=200)
    variables: dict[str, str | int | float | bool] = Field(default_factory=dict)


class AssignAcknowledgementRequest(OrganizationRequest):
    assigned_employee_id: UUID
