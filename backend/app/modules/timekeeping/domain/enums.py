"""Timekeeping enumerations persisted as stable string values."""

from enum import StrEnum


class LeaveCategory(StrEnum):
    """Broad family a configurable leave type belongs to.

    The category drives system behaviour (balance checks, medical confirmation);
    organizations add their own leave types on top of these families.
    """

    ANNUAL = "annual"
    SICK = "sick"
    UNPAID = "unpaid"
    DAY_OFF = "day_off"
    PARENTAL = "parental"
    STUDY = "study"
    OTHER = "other"


class LeaveRequestStatus(StrEnum):
    """Mirrors the shared process states in section 3 of the MVP plan."""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    UNDER_APPROVAL = "under_approval"
    AWAITING_SIGNATURE = "awaiting_signature"
    APPROVED = "approved"
    RETURNED = "returned"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveLedgerEntryType(StrEnum):
    """Append-only ledger movements; balances are never overwritten in place."""

    ACCRUAL = "accrual"
    CARRY_OVER = "carry_over"
    BOOKING = "booking"
    RELEASE = "release"
    CORRECTION = "correction"
    EXPIRY = "expiry"
    PAYOUT = "payout"


class TimeCodeCategory(StrEnum):
    """Determines how a timesheet entry is interpreted downstream."""

    WORK = "work"
    OVERTIME = "overtime"
    NIGHT = "night"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"
    LEAVE = "leave"
    SICK = "sick"
    BUSINESS_TRIP = "business_trip"
    ABSENCE = "absence"
    UNPAID_ABSENCE = "unpaid_absence"


class TimesheetPeriodStatus(StrEnum):
    """Section 8: HR closes the period, then hands it to accounting."""

    OPEN = "open"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    SENT_TO_ACCOUNTING = "sent_to_accounting"
    REOPENED = "reopened"


class TimesheetEntrySource(StrEnum):
    """Provenance of a timesheet row.

    Section 8 forbids typing a timesheet from scratch: rows are derived from the
    schedule and from approved events, and anything manual carries a reason.
    """

    SCHEDULE = "schedule"
    ABSENCE = "absence"
    LEAVE_REQUEST = "leave_request"
    BUSINESS_TRIP = "business_trip"
    MANUAL = "manual"
    CORRECTION = "correction"


class TimesheetCorrectionStatus(StrEnum):
    """The separate correction process required once a period is closed."""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    UNDER_APPROVAL = "under_approval"
    APPLIED = "applied"
    RETURNED = "returned"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class WorkScheduleKind(StrEnum):
    FIVE_DAY = "five_day"
    SIX_DAY = "six_day"
    SHIFT = "shift"
    FLEXIBLE = "flexible"
    SUMMARIZED = "summarized"
