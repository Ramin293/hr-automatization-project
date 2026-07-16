from enum import StrEnum


class DefinitionVersionStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StepType(StrEnum):
    DATA_ENTRY = "data_entry"
    COMPLETENESS_CHECK = "completeness_check"
    APPROVAL = "approval"
    REVIEW = "review"
    INTERVIEW = "interview"
    COMMISSION_DECISION = "commission_decision"
    DOCUMENT_PREPARATION = "document_preparation"
    SIGNATURE = "signature"
    REGISTRATION = "registration"
    ACKNOWLEDGEMENT = "acknowledgement"
    PARALLEL_TASK = "parallel_task"
    FINAL_COMPLETION = "final_completion"


class ActorRuleType(StrEnum):
    INITIATOR = "process_initiator"
    REQUESTING_UNIT_HEAD = "requesting_unit_head"
    SUBJECT_EMPLOYEE = "subject_employee"
    SUBJECT_EMPLOYEE_MANAGER = "subject_employee_manager"
    FUNCTIONAL_ROLE = "functional_role"
    PERMISSION_HOLDER = "permission_holder"
    ORGANIZATION_ROLE = "organization_role"
    COMMISSION_MEMBERS = "commission_members"
    SIGNING_AUTHORITY = "signing_authority"
    EXPLICIT_USER = "explicit_user"


class ProcessStatus(StrEnum):
    ACTIVE = "active"
    CONFIGURATION_ERROR = "configuration_error"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    RETURNED = "returned"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CompletionMode(StrEnum):
    ALL = "all"
    ANY = "any"


ALLOWED_ACTIONS = frozenset(
    {"submit", "approve", "return", "reject", "complete", "cancel", "reopen"}
)
