from enum import StrEnum


class DocumentStatus(StrEnum):
    DRAFT = "draft"
    UPLOADED = "uploaded"
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    AWAITING_SIGNATURE = "awaiting_signature"
    SIGNED = "signed"
    REJECTED = "rejected"
    REGISTERED = "registered"
    ACKNOWLEDGED = "acknowledged"
    ARCHIVED = "archived"
    VOIDED = "voided"


class SignatureStatus(StrEnum):
    NOT_REQUESTED = "not_requested"
    PENDING_EXTERNAL = "pending_external"
    SIGNED = "signed"
    REJECTED = "rejected"
    FAILED = "failed"


class TemplateStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
