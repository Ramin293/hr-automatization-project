from uuid import uuid4

from app.modules.workflow.domain.entities import (
    ProcessStepDefinition,
    ProcessTransitionDefinition,
    validate_condition,
    validate_definition,
)
from app.modules.workflow.domain.enums import CompletionMode, StepType
from app.modules.workflow.infrastructure.operations import _condition_matches


def _step(code: str, sequence: int) -> ProcessStepDefinition:
    return ProcessStepDefinition(
        definition_version_id=uuid4(),
        stable_key=uuid4(),
        code=code,
        name=code,
        step_type=StepType.APPROVAL,
        sequence=sequence,
        actor_rule_id=None,
        allowed_actions=("approve", "return", "reject"),
        completion_mode=CompletionMode.ALL,
    )


def test_valid_definition_and_safe_condition() -> None:
    first, second = _step("first", 0), _step("second", 1)
    transition = ProcessTransitionDefinition(
        definition_version_id=first.definition_version_id,
        source_step_id=first.id,
        target_step_id=second.id,
        action="approve",
        condition={
            "and": [
                {"eq": {"field": "request.kind", "value": "standard"}},
                {"gte": {"field": "request.fte", "value": 1}},
            ]
        },
    )
    assert validate_definition([first, second], [transition]) == ()
    assert _condition_matches(transition.condition, {"request": {"kind": "standard", "fte": 1}})


def test_invalid_expression_and_unreachable_step_are_rejected() -> None:
    first, second, orphan = _step("first", 0), _step("second", 1), _step("orphan", 2)
    transition = ProcessTransitionDefinition(
        definition_version_id=first.definition_version_id,
        source_step_id=first.id,
        target_step_id=second.id,
        action="approve",
        condition={"python": "__import__('os')"},
    )
    problems = validate_definition([first, second, orphan], [transition])
    assert not validate_condition(transition.condition)
    assert {item.code for item in problems} >= {"INVALID_TRANSITION", "INVALID_START_STEP"}


def test_self_cycle_is_rejected() -> None:
    step = _step("single", 0)
    transition = ProcessTransitionDefinition(
        definition_version_id=step.definition_version_id,
        source_step_id=step.id,
        target_step_id=step.id,
        action="approve",
    )
    assert "TRANSITION_SELF_CYCLE" in {
        item.code for item in validate_definition([step], [transition])
    }
