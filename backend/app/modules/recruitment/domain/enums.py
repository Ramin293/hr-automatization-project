from enum import StrEnum


class RecruitmentRequestStatus(StrEnum):
    DRAFT = "draft"
    HR_REVIEW = "hr_review"
    STAFFING_REVIEW = "staffing_review"
    RETURNED = "returned"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    VACANCY_CREATED = "vacancy_created"
    COMPLETED = "completed"


class VacancyStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    OPEN_INTERNAL = "open_internal"
    OPEN_EXTERNAL = "open_external"
    PAUSED = "paused"
    SELECTION = "selection"
    OFFER = "offer"
    FILLED = "filled"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class ApplicationStatus(StrEnum):
    RECEIVED = "received"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    COMMISSION_REVIEW = "commission_review"
    SELECTED = "selected"
    RESERVE = "reserve"
    OFFER_PENDING = "offer_pending"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    HIRED = "hired"


class OfferStatus(StrEnum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class HiringStatus(StrEnum):
    DOCUMENT_COLLECTION = "document_collection"
    DOCUMENT_REVIEW = "document_review"
    CONTRACT_PREPARATION = "contract_preparation"
    CONTRACT_SIGNATURE = "contract_signature"
    ORDER_PREPARATION = "order_preparation"
    ORDER_SIGNATURE = "order_signature"
    REGISTRATION = "registration"
    ONBOARDING = "onboarding"
    COMPLETED = "completed"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    FAILED = "failed"
