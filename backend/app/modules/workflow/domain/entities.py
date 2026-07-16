from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.shared.identifiers import new_uuid
from app.shared.time import utc_now

from .enums import (
    ALLOWED_ACTIONS,
    ActorRuleType,
    CompletionMode,
    DefinitionVersionStatus,
    ProcessStatus,
    StepType,
    TaskStatus,
)


@dataclass(slots=True)
class ProcessDefinition:
    organization_id: UUID
    code: str
    name: str
    description: str | None = None
    active: bool = True
    id: UUID = field(default_factory=new_uuid)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ProcessDefinitionVersion:
    process_definition_id: UUID
    version_number: int
    name: str
    created_by: UUID
    status: DefinitionVersionStatus = DefinitionVersionStatus.DRAFT
    based_on_version_id: UUID | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    revision: int = 1
    published_by: UUID | None = None
    id: UUID = field(default_factory=new_uuid)
    created_at: datetime = field(default_factory=utc_now)
    published_at: datetime | None = None

    def assert_editable(self) -> None:
        if self.status is not DefinitionVersionStatus.DRAFT:
            raise ValueError("Only workflow definition drafts are editable.")


@dataclass(slots=True)
class ActorRule:
    definition_version_id: UUID
    code: str
    name: str
    rule_type: ActorRuleType
    configuration: dict[str, Any]
    active: bool = True
    revision: int = 1
    id: UUID = field(default_factory=new_uuid)


@dataclass(slots=True)
class ProcessStepDefinition:
    definition_version_id: UUID
    stable_key: UUID
    code: str
    name: str
    step_type: StepType
    sequence: int
    actor_rule_id: UUID | None
    allowed_actions: tuple[str, ...]
    due_duration: timedelta | None = None
    required_document_type_ids: tuple[UUID, ...] = ()
    configuration: dict[str, Any] = field(default_factory=dict)
    completion_mode: CompletionMode = CompletionMode.ALL
    required_approvers: int = 1
    active: bool = True
    revision: int = 1
    id: UUID = field(default_factory=new_uuid)


@dataclass(slots=True)
class ProcessTransitionDefinition:
    definition_version_id: UUID
    source_step_id: UUID
    target_step_id: UUID
    action: str
    condition: dict[str, Any] | None = None
    priority: int = 0
    active: bool = True
    id: UUID = field(default_factory=new_uuid)


@dataclass(frozen=True, slots=True)
class ConfigurationProblem:
    code: str
    message: str
    entity_id: UUID | None = None


SAFE_CONDITION_OPERATORS = frozenset(
    {"eq", "ne", "in", "not_in", "exists", "gt", "gte", "lt", "lte", "and", "or"}
)


def validate_condition(condition: Any) -> bool:
    if condition is None:
        return True
    if not isinstance(condition, dict) or len(condition) != 1:
        return False
    operator, value = next(iter(condition.items()))
    if operator not in SAFE_CONDITION_OPERATORS:
        return False
    if operator in {"and", "or"}:
        return (
            isinstance(value, list)
            and bool(value)
            and all(validate_condition(item) for item in value)
        )
    return (
        isinstance(value, dict) and "field" in value and (operator == "exists" or "value" in value)
    )


def validate_definition(
    steps: list[ProcessStepDefinition], transitions: list[ProcessTransitionDefinition]
) -> tuple[ConfigurationProblem, ...]:
    problems: list[ConfigurationProblem] = []
    active_steps = {step.id: step for step in steps if step.active}
    codes: set[str] = set()
    for step in active_steps.values():
        if step.code in codes:
            problems.append(
                ConfigurationProblem("DUPLICATE_STEP_CODE", "Step codes must be unique.", step.id)
            )
        codes.add(step.code)
        if not step.allowed_actions or any(
            action not in ALLOWED_ACTIONS for action in step.allowed_actions
        ):
            problems.append(
                ConfigurationProblem(
                    "INVALID_STEP_ACTION", "The step contains an unsupported action.", step.id
                )
            )
        if step.required_approvers < 1:
            problems.append(
                ConfigurationProblem(
                    "INVALID_APPROVER_COUNT", "requiredApprovers must be positive.", step.id
                )
            )
    incoming = {step_id: 0 for step_id in active_steps}
    graph: dict[UUID, set[UUID]] = {step_id: set() for step_id in active_steps}
    for transition in transitions:
        if not transition.active:
            continue
        if (
            transition.source_step_id not in active_steps
            or transition.target_step_id not in active_steps
        ):
            problems.append(
                ConfigurationProblem(
                    "INVALID_TRANSITION_REFERENCE",
                    "Transition references a missing step.",
                    transition.id,
                )
            )
            continue
        if transition.source_step_id == transition.target_step_id:
            problems.append(
                ConfigurationProblem(
                    "TRANSITION_SELF_CYCLE",
                    "A transition cannot target its source step.",
                    transition.id,
                )
            )
        if transition.action not in ALLOWED_ACTIONS or not validate_condition(transition.condition):
            problems.append(
                ConfigurationProblem(
                    "INVALID_TRANSITION",
                    "Transition action or condition is invalid.",
                    transition.id,
                )
            )
        graph[transition.source_step_id].add(transition.target_step_id)
        incoming[transition.target_step_id] += 1
    roots = [step_id for step_id, count in incoming.items() if count == 0]
    if len(roots) != 1:
        problems.append(
            ConfigurationProblem(
                "INVALID_START_STEP", "A process must have exactly one reachable start step."
            )
        )
    if roots:
        visited: set[UUID] = set()
        stack = [roots[0]]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(graph[current])
        for step_id in active_steps.keys() - visited:
            problems.append(
                ConfigurationProblem("UNREACHABLE_STEP", "The step is unreachable.", step_id)
            )
    return tuple(problems)


@dataclass(slots=True)
class ProcessInstance:
    organization_id: UUID
    process_definition_id: UUID
    definition_version_id: UUID
    business_type: str
    business_entity_id: UUID
    initiator_user_id: UUID
    snapshot: dict[str, Any]
    status: ProcessStatus = ProcessStatus.ACTIVE
    current_phase: str | None = None
    revision: int = 1
    id: UUID = field(default_factory=new_uuid)
    started_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


@dataclass(slots=True)
class WorkflowTask:
    process_instance_id: UUID
    step_definition_id: UUID
    assigned_user_id: UUID | None = None
    assigned_employee_id: UUID | None = None
    assigned_unit_id: UUID | None = None
    status: TaskStatus = TaskStatus.ACTIVE
    due_at: datetime | None = None
    decision: str | None = None
    decision_comment: str | None = None
    idempotency_key: str | None = None
    revision: int = 1
    id: UUID = field(default_factory=new_uuid)
    created_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ProcessHistoryEntry:
    process_instance_id: UUID
    event_type: str
    actor_user_id: UUID | None
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=new_uuid)
    occurred_at: datetime = field(default_factory=utc_now)
