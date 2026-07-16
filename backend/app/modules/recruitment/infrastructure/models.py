from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.database.mixins import RevisionMixin, TimestampMixin, UUIDPrimaryKeyMixin


class RecruitmentRequestModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "recruitment_requests"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    requesting_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"), index=True
    )
    requested_by_employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    staffing_slot_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("staffing_slots.id", ondelete="RESTRICT")
    )
    position_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("position_definitions.id", ondelete="RESTRICT")
    )
    requested_fte: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    employment_type: Mapped[str] = mapped_column(String(50))
    desired_start_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    responsibilities: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text)
    proposed_compensation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )


class StaffingReviewModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "recruitment_staffing_reviews"
    __table_args__ = (UniqueConstraint("recruitment_request_id"),)
    recruitment_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("recruitment_requests.id", ondelete="RESTRICT")
    )
    reviewer_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    vacant_slot_confirmed: Mapped[bool] = mapped_column(Boolean)
    approved_fte: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    budget_confirmed: Mapped[bool] = mapped_column(Boolean)
    compensation_range: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    decision: Mapped[str] = mapped_column(String(30))
    comment: Mapped[str] = mapped_column(Text)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class VacancyModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "vacancies"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    recruitment_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("recruitment_requests.id", ondelete="RESTRICT")
    )
    staffing_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("staffing_slots.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    responsibilities: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text)
    employment_conditions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    publication_status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    internal_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    application_deadline: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    close_reason: Mapped[str | None] = mapped_column(Text)


class PublicationChannelModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "vacancy_publication_channels"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    channel_type: Mapped[str] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class VacancyPublicationModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "vacancy_publications"
    __table_args__ = (UniqueConstraint("vacancy_id", "channel_id"),)
    vacancy_id: Mapped[UUID] = mapped_column(ForeignKey("vacancies.id", ondelete="RESTRICT"))
    channel_id: Mapped[UUID] = mapped_column(
        ForeignKey("vacancy_publication_channels.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30))
    external_reference: Mapped[str | None] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    responsible_employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    manual: Mapped[bool] = mapped_column(Boolean, default=True)


class CandidateModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "candidates"
    __table_args__ = (Index("ix_candidates_org_status", "organization_id", "status"),)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    first_name: Mapped[str] = mapped_column(String(160))
    last_name: Mapped[str] = mapped_column(String(160))
    middle_name: Mapped[str | None] = mapped_column(String(160))
    display_name: Mapped[str] = mapped_column(String(500))
    protected_personal_email: Mapped[str | None] = mapped_column(Text)
    protected_phone: Mapped[str | None] = mapped_column(Text)
    protected_identity: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    consent_status: Mapped[str] = mapped_column(String(30))
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_until: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="active")
    anonymized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CandidateApplicationModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "candidate_applications"
    __table_args__ = (UniqueConstraint("candidate_id", "vacancy_id"),)
    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="RESTRICT"), index=True
    )
    vacancy_id: Mapped[UUID] = mapped_column(
        ForeignKey("vacancies.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_stage: Mapped[str] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(100))
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason_code: Mapped[str | None] = mapped_column(String(100))
    rejection_comment: Mapped[str | None] = mapped_column(Text)


class ScreeningModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "candidate_screenings"
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="RESTRICT"), index=True
    )
    reviewer_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="RESTRICT")
    )
    criteria_results: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    decision: Mapped[str] = mapped_column(String(30))
    comment: Mapped[str] = mapped_column(Text)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InterviewModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "interviews"
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="RESTRICT"), index=True
    )
    round_number: Mapped[int] = mapped_column(Integer)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    format: Mapped[str] = mapped_column(String(30))
    location_reference: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(30))
    restricted_notes: Mapped[str | None] = mapped_column(Text)


class InterviewParticipantModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "interview_participants"
    __table_args__ = (UniqueConstraint("interview_id", "employee_id"),)
    interview_id: Mapped[UUID] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"))
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"))
    role: Mapped[str] = mapped_column(String(50))
    required: Mapped[bool] = mapped_column(Boolean, default=True)


class InterviewEvaluationModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "interview_evaluations"
    __table_args__ = (
        UniqueConstraint("interview_id", "interviewer_employee_id", "version_number"),
    )
    interview_id: Mapped[UUID] = mapped_column(ForeignKey("interviews.id", ondelete="RESTRICT"))
    interviewer_employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    criteria_results: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    recommendation: Mapped[str] = mapped_column(String(50))
    comment: Mapped[str] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    amended_from_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("interview_evaluations.id", ondelete="RESTRICT")
    )


class CommissionModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "competition_commissions"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    code: Mapped[str] = mapped_column(String(100))
    meeting_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quorum_required: Mapped[int] = mapped_column(Integer)
    protocol_document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30))


class CommissionMemberModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "competition_commission_members"
    __table_args__ = (UniqueConstraint("commission_id", "employee_id"),)
    commission_id: Mapped[UUID] = mapped_column(
        ForeignKey("competition_commissions.id", ondelete="CASCADE")
    )
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"))
    role: Mapped[str] = mapped_column(String(30))
    conflict_declared: Mapped[bool] = mapped_column(Boolean, default=False)
    declaration: Mapped[str | None] = mapped_column(Text)


class CommissionDecisionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "competition_commission_decisions"
    __table_args__ = (UniqueConstraint("commission_id", "application_id"),)
    commission_id: Mapped[UUID] = mapped_column(
        ForeignKey("competition_commissions.id", ondelete="RESTRICT")
    )
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="RESTRICT")
    )
    decision: Mapped[str] = mapped_column(String(50))
    comment: Mapped[str] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class JobOfferModel(UUIDPrimaryKeyMixin, RevisionMixin, TimestampMixin, Base):
    __tablename__ = "job_offers"
    __table_args__ = (UniqueConstraint("application_id"),)
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="RESTRICT")
    )
    position_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("position_definitions.id", ondelete="RESTRICT")
    )
    staffing_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("staffing_slots.id", ondelete="RESTRICT")
    )
    proposed_conditions: Mapped[dict[str, Any]] = mapped_column(JSONB)
    proposed_start_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    declined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decline_reason: Mapped[str | None] = mapped_column(Text)
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_records.id", ondelete="RESTRICT")
    )


class HiringCaseModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "hiring_cases"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    candidate_application_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidate_applications.id", ondelete="RESTRICT"), unique=True
    )
    recruitment_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("recruitment_requests.id", ondelete="RESTRICT")
    )
    staffing_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("staffing_slots.id", ondelete="RESTRICT")
    )
    proposed_start_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), index=True)
    process_instance_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("process_instances.id", ondelete="RESTRICT")
    )
    person_id: Mapped[UUID | None] = mapped_column(ForeignKey("people.id", ondelete="RESTRICT"))
    employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    assignment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employee_assignments.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OnboardingTaskModel(UUIDPrimaryKeyMixin, RevisionMixin, Base):
    __tablename__ = "onboarding_tasks"
    hiring_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("hiring_cases.id", ondelete="CASCADE"), index=True
    )
    task_type: Mapped[str] = mapped_column(String(50))
    assigned_unit_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT")
    )
    assigned_employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion_evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
