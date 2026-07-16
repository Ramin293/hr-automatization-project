from decimal import Decimal

import pytest
from app.core.errors import ValidationError
from app.core.errors.codes import ErrorCode
from app.modules.recruitment.domain.rules import (
    require_candidate_consent,
    require_commission_quorum,
    require_vacant_slot,
)


def test_candidate_consent_is_required() -> None:
    with pytest.raises(ValidationError) as error:
        require_candidate_consent("withdrawn")
    assert error.value.code == ErrorCode.CANDIDATE_CONSENT_REQUIRED


def test_staffing_capacity_and_commission_quorum() -> None:
    with pytest.raises(ValidationError) as capacity:
        require_vacant_slot(
            slot_status="vacant",
            requested_fte=Decimal("0.75"),
            slot_fte=Decimal("1"),
            occupied_fte=Decimal("0.5"),
        )
    assert capacity.value.code == ErrorCode.STAFFING_SLOT_CAPACITY_EXCEEDED
    with pytest.raises(ValidationError) as quorum:
        require_commission_quorum(eligible_members=2, quorum_required=3)
    assert quorum.value.code == ErrorCode.COMMISSION_QUORUM_NOT_REACHED
