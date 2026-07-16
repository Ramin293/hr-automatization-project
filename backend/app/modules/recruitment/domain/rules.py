from __future__ import annotations

from decimal import Decimal

from app.core.errors import ValidationError
from app.core.errors.codes import ErrorCode


def require_candidate_consent(status: str) -> None:
    if status != "granted":
        raise ValidationError(
            "Candidate consent is required.", code=ErrorCode.CANDIDATE_CONSENT_REQUIRED
        )


def require_vacant_slot(
    *, slot_status: str, requested_fte: Decimal, slot_fte: Decimal, occupied_fte: Decimal
) -> None:
    if slot_status not in {"approved", "vacant", "occupied"}:
        raise ValidationError(
            "An approved vacant staffing slot is required.", code=ErrorCode.STAFFING_SLOT_NOT_VACANT
        )
    if occupied_fte + requested_fte > slot_fte:
        raise ValidationError(
            "The staffing slot capacity would be exceeded.",
            code=ErrorCode.STAFFING_SLOT_CAPACITY_EXCEEDED,
        )


def require_commission_quorum(*, eligible_members: int, quorum_required: int) -> None:
    if eligible_members < quorum_required:
        raise ValidationError(
            "Commission quorum was not reached.", code=ErrorCode.COMMISSION_QUORUM_NOT_REACHED
        )
