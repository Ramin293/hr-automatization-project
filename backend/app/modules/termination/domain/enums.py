from enum import StrEnum


class TerminationStatus(StrEnum):
    DRAFT = "draft"
    HR_REVIEW = "hr_review"
    LEGAL_REVIEW = "legal_review"
    SIGNATURE = "signature"
    REGISTRATION = "registration"
    OFFBOARDING = "offboarding"
    SCHEDULED = "scheduled"
    EFFECTIVE = "effective"
    COMPLETED = "completed"
    RETURNED = "returned"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class OffboardingTaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    WAIVED = "waived"
    CANCELLED = "cancelled"
