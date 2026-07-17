"""module4 timekeeping: timesheets and leave

Also merges the two heads left by 0004_employee_absences and 0004_module2: this
revision needs tables from both (employee_absences, document_records).

Revision ID: 0005_module4_timekeeping
Revises: 0004_employee_absences, 0004_module2
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_module4_timekeeping"
down_revision: tuple[str, ...] = ("0004_employee_absences", "0004_module2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "time_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("paid", sa.Boolean(), nullable=False),
        sa.Column("counts_as_worked_time", sa.Boolean(), nullable=False),
        sa.Column("external_code", sa.String(length=50), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_time_codes_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_time_codes")),
        sa.UniqueConstraint("organization_id", "code", name="uq_time_codes_organization_code"),
    )
    op.create_index(op.f("ix_time_codes_organization_id"), "time_codes", ["organization_id"])
    op.create_index(
        "ix_time_codes_organization_active", "time_codes", ["organization_id", "active"]
    )

    op.create_table(
        "leave_types",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("paid", sa.Boolean(), nullable=False),
        sa.Column("consumes_balance", sa.Boolean(), nullable=False),
        sa.Column("requires_manager_approval", sa.Boolean(), nullable=False),
        sa.Column("requires_supporting_document", sa.Boolean(), nullable=False),
        sa.Column("requires_order_document", sa.Boolean(), nullable=False),
        sa.Column("default_annual_days", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("max_carry_over_days", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("min_notice_days", sa.Integer(), nullable=True),
        sa.Column("time_code_id", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "default_annual_days IS NULL OR default_annual_days >= 0",
            name=op.f("ck_leave_types_default_days_nonnegative"),
        ),
        sa.CheckConstraint(
            "max_carry_over_days IS NULL OR max_carry_over_days >= 0",
            name=op.f("ck_leave_types_carry_over_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_leave_types_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_leave_types_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leave_types")),
        sa.UniqueConstraint("organization_id", "code", name="uq_leave_types_organization_code"),
    )
    op.create_index(op.f("ix_leave_types_organization_id"), "leave_types", ["organization_id"])
    op.create_index(
        "ix_leave_types_organization_active", "leave_types", ["organization_id", "active"]
    )

    op.create_table(
        "leave_entitlements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("leave_type_id", sa.Uuid(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("granted_days", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("basis", sa.Text(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "period_end >= period_start", name=op.f("ck_leave_entitlements_valid_period")
        ),
        sa.CheckConstraint(
            "granted_days >= 0", name=op.f("ck_leave_entitlements_granted_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_leave_entitlements_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_leave_entitlements_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["leave_type_id"],
            ["leave_types.id"],
            name=op.f("fk_leave_entitlements_leave_type_id_leave_types"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leave_entitlements")),
        sa.UniqueConstraint(
            "employee_id",
            "leave_type_id",
            "period_start",
            name="uq_leave_entitlements_employee_type_period",
        ),
    )
    op.create_index(
        op.f("ix_leave_entitlements_organization_id"), "leave_entitlements", ["organization_id"]
    )
    op.create_index(
        op.f("ix_leave_entitlements_employee_id"), "leave_entitlements", ["employee_id"]
    )
    op.create_index(
        "ix_leave_entitlements_employee_period",
        "leave_entitlements",
        ["employee_id", "period_start", "period_end"],
    )

    op.create_table(
        "work_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("cycle_length_days", sa.Integer(), nullable=False),
        sa.Column("weekly_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("default_time_code_id", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("cycle_length_days > 0", name=op.f("ck_work_schedules_cycle_positive")),
        sa.CheckConstraint(
            "weekly_hours IS NULL OR weekly_hours > 0",
            name=op.f("ck_work_schedules_weekly_hours_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_work_schedules_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["default_time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_work_schedules_default_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_schedules")),
        sa.UniqueConstraint("organization_id", "code", name="uq_work_schedules_organization_code"),
    )
    op.create_index(
        op.f("ix_work_schedules_organization_id"), "work_schedules", ["organization_id"]
    )

    op.create_table(
        "work_schedule_days",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("work_schedule_id", sa.Uuid(), nullable=False),
        sa.Column("cycle_day", sa.Integer(), nullable=False),
        sa.Column("working_day", sa.Boolean(), nullable=False),
        sa.Column("hours", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("starts_at_minute", sa.Integer(), nullable=True),
        sa.Column("time_code_id", sa.Uuid(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "cycle_day >= 0", name=op.f("ck_work_schedule_days_cycle_day_nonnegative")
        ),
        sa.CheckConstraint("hours >= 0", name=op.f("ck_work_schedule_days_hours_nonnegative")),
        sa.ForeignKeyConstraint(
            ["work_schedule_id"],
            ["work_schedules.id"],
            name=op.f("fk_work_schedule_days_work_schedule_id_work_schedules"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_work_schedule_days_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_schedule_days")),
        sa.UniqueConstraint(
            "work_schedule_id", "cycle_day", name="uq_work_schedule_days_schedule_day"
        ),
    )
    op.create_index(
        op.f("ix_work_schedule_days_work_schedule_id"), "work_schedule_days", ["work_schedule_id"]
    )

    op.create_table(
        "employee_work_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("work_schedule_id", sa.Uuid(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("cycle_anchor_date", sa.Date(), nullable=True),
        sa.Column("assigned_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name=op.f("ck_employee_work_schedules_valid_dates"),
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_employee_work_schedules_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["work_schedule_id"],
            ["work_schedules.id"],
            name=op.f("fk_employee_work_schedules_work_schedule_id_work_schedules"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_employee_work_schedules_assigned_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employee_work_schedules")),
    )
    op.create_index(
        op.f("ix_employee_work_schedules_employee_id"), "employee_work_schedules", ["employee_id"]
    )
    op.create_index(
        "ix_employee_work_schedules_employee_effective",
        "employee_work_schedules",
        ["employee_id", "effective_from", "effective_to"],
    )

    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("leave_type_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("requested_days", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("half_day_start", sa.Boolean(), nullable=False),
        sa.Column("half_day_end", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("process_instance_id", sa.Uuid(), nullable=True),
        sa.Column("order_document_id", sa.Uuid(), nullable=True),
        sa.Column("absence_id", sa.Uuid(), nullable=True),
        sa.Column("substitute_employee_id", sa.Uuid(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("date_to >= date_from", name=op.f("ck_leave_requests_valid_dates")),
        sa.CheckConstraint("requested_days > 0", name=op.f("ck_leave_requests_days_positive")),
        postgresql.ExcludeConstraint(
            (sa.column("employee_id"), "="),
            (sa.text("daterange(date_from, date_to, '[]')"), "&&"),
            where=sa.text(
                "status IN ('under_review', 'under_approval', 'awaiting_signature', 'approved')"
            ),
            using="gist",
            name="ex_leave_requests_no_overlap_per_employee",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_leave_requests_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_leave_requests_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["leave_type_id"],
            ["leave_types.id"],
            name=op.f("fk_leave_requests_leave_type_id_leave_types"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_leave_requests_requested_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["process_instance_id"],
            ["process_instances.id"],
            name=op.f("fk_leave_requests_process_instance_id_process_instances"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["order_document_id"],
            ["document_records.id"],
            name=op.f("fk_leave_requests_order_document_id_document_records"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["absence_id"],
            ["employee_absences.id"],
            name=op.f("fk_leave_requests_absence_id_employee_absences"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["substitute_employee_id"],
            ["employees.id"],
            name=op.f("fk_leave_requests_substitute_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_leave_requests_decided_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leave_requests")),
    )
    op.create_index(
        op.f("ix_leave_requests_organization_id"), "leave_requests", ["organization_id"]
    )
    op.create_index(op.f("ix_leave_requests_employee_id"), "leave_requests", ["employee_id"])
    op.create_index(op.f("ix_leave_requests_status"), "leave_requests", ["status"])
    op.create_index(
        "ix_leave_requests_employee_dates",
        "leave_requests",
        ["employee_id", "date_from", "date_to"],
    )
    op.create_index(
        "ix_leave_requests_scope_status",
        "leave_requests",
        ["organization_id", "status", "date_from"],
    )
    op.create_index(
        "ix_leave_requests_process_instance", "leave_requests", ["process_instance_id"]
    )

    op.create_table(
        "leave_balance_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("leave_type_id", sa.Uuid(), nullable=False),
        sa.Column("entitlement_id", sa.Uuid(), nullable=True),
        sa.Column("entry_type", sa.String(length=30), nullable=False),
        sa.Column("days", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("leave_request_id", sa.Uuid(), nullable=True),
        sa.Column("reverses_entry_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("days <> 0", name=op.f("ck_leave_balance_entries_days_nonzero")),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_leave_balance_entries_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_leave_balance_entries_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["leave_type_id"],
            ["leave_types.id"],
            name=op.f("fk_leave_balance_entries_leave_type_id_leave_types"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["entitlement_id"],
            ["leave_entitlements.id"],
            name=op.f("fk_leave_balance_entries_entitlement_id_leave_entitlements"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["leave_request_id"],
            ["leave_requests.id"],
            name=op.f("fk_leave_balance_entries_leave_request_id_leave_requests"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reverses_entry_id"],
            ["leave_balance_entries.id"],
            name=op.f("fk_leave_balance_entries_reverses_entry_id_leave_balance_entries"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["user_accounts.id"],
            name=op.f("fk_leave_balance_entries_created_by_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leave_balance_entries")),
    )
    op.create_index(
        op.f("ix_leave_balance_entries_organization_id"),
        "leave_balance_entries",
        ["organization_id"],
    )
    op.create_index(
        op.f("ix_leave_balance_entries_employee_id"), "leave_balance_entries", ["employee_id"]
    )
    op.create_index(
        "ix_leave_balance_entries_employee_type",
        "leave_balance_entries",
        ["employee_id", "leave_type_id", "occurred_at"],
    )
    op.create_index(
        "ix_leave_balance_entries_entitlement", "leave_balance_entries", ["entitlement_id"]
    )

    op.create_table(
        "timesheet_periods",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("organization_unit_id", sa.Uuid(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("manager_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("manager_confirmed_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("sent_to_accounting_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopen_reason", sa.Text(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "period_end >= period_start", name=op.f("ck_timesheet_periods_valid_dates")
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_timesheet_periods_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["organization_unit_id"],
            ["organization_units.id"],
            name=op.f("fk_timesheet_periods_organization_unit_id_organization_units"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["manager_confirmed_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_timesheet_periods_manager_confirmed_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["closed_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_timesheet_periods_closed_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timesheet_periods")),
        sa.UniqueConstraint(
            "organization_unit_id", "period_start", name="uq_timesheet_periods_unit_period"
        ),
    )
    op.create_index(
        op.f("ix_timesheet_periods_organization_id"), "timesheet_periods", ["organization_id"]
    )
    op.create_index(
        op.f("ix_timesheet_periods_organization_unit_id"),
        "timesheet_periods",
        ["organization_unit_id"],
    )
    op.create_index(op.f("ix_timesheet_periods_status"), "timesheet_periods", ["status"])
    op.create_index(
        "ix_timesheet_periods_scope_status",
        "timesheet_periods",
        ["organization_id", "status", "period_start"],
    )

    op.create_table(
        "timesheet_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("timesheet_period_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("time_code_id", sa.Uuid(), nullable=False),
        sa.Column("hours", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("source_absence_id", sa.Uuid(), nullable=True),
        sa.Column("source_leave_request_id", sa.Uuid(), nullable=True),
        sa.Column("manual_reason", sa.Text(), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("hours >= 0", name=op.f("ck_timesheet_entries_hours_nonnegative")),
        sa.CheckConstraint("hours <= 24", name=op.f("ck_timesheet_entries_hours_maximum")),
        sa.CheckConstraint(
            "(source IN ('manual', 'correction')) = (manual_reason IS NOT NULL)",
            name=op.f("ck_timesheet_entries_manual_reason_present"),
        ),
        sa.ForeignKeyConstraint(
            ["timesheet_period_id"],
            ["timesheet_periods.id"],
            name=op.f("fk_timesheet_entries_timesheet_period_id_timesheet_periods"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_timesheet_entries_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_timesheet_entries_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_absence_id"],
            ["employee_absences.id"],
            name=op.f("fk_timesheet_entries_source_absence_id_employee_absences"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_leave_request_id"],
            ["leave_requests.id"],
            name=op.f("fk_timesheet_entries_source_leave_request_id_leave_requests"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_timesheet_entries_created_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timesheet_entries")),
        sa.UniqueConstraint(
            "timesheet_period_id",
            "employee_id",
            "entry_date",
            "time_code_id",
            name="uq_timesheet_entries_period_employee_date_code",
        ),
    )
    op.create_index(
        op.f("ix_timesheet_entries_timesheet_period_id"),
        "timesheet_entries",
        ["timesheet_period_id"],
    )
    op.create_index(op.f("ix_timesheet_entries_employee_id"), "timesheet_entries", ["employee_id"])
    op.create_index(
        "ix_timesheet_entries_employee_date", "timesheet_entries", ["employee_id", "entry_date"]
    )
    op.create_index(
        "ix_timesheet_entries_period_employee",
        "timesheet_entries",
        ["timesheet_period_id", "employee_id"],
    )

    op.create_table(
        "timesheet_corrections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("timesheet_period_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("timesheet_entry_id", sa.Uuid(), nullable=True),
        sa.Column("previous_time_code_id", sa.Uuid(), nullable=True),
        sa.Column("previous_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("requested_time_code_id", sa.Uuid(), nullable=True),
        sa.Column("requested_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("process_instance_id", sa.Uuid(), nullable=True),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "requested_hours IS NULL OR requested_hours >= 0",
            name=op.f("ck_timesheet_corrections_requested_hours_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_timesheet_corrections_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["timesheet_period_id"],
            ["timesheet_periods.id"],
            name=op.f("fk_timesheet_corrections_timesheet_period_id_timesheet_periods"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_timesheet_corrections_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["timesheet_entry_id"],
            ["timesheet_entries.id"],
            name=op.f("fk_timesheet_corrections_timesheet_entry_id_timesheet_entries"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["previous_time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_timesheet_corrections_previous_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requested_time_code_id"],
            ["time_codes.id"],
            name=op.f("fk_timesheet_corrections_requested_time_code_id_time_codes"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["process_instance_id"],
            ["process_instances.id"],
            name=op.f("fk_timesheet_corrections_process_instance_id_process_instances"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_timesheet_corrections_requested_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["applied_by_user_id"],
            ["user_accounts.id"],
            name=op.f("fk_timesheet_corrections_applied_by_user_id_user_accounts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timesheet_corrections")),
    )
    op.create_index(
        op.f("ix_timesheet_corrections_organization_id"),
        "timesheet_corrections",
        ["organization_id"],
    )
    op.create_index(
        op.f("ix_timesheet_corrections_employee_id"), "timesheet_corrections", ["employee_id"]
    )
    op.create_index(op.f("ix_timesheet_corrections_status"), "timesheet_corrections", ["status"])
    op.create_index(
        "ix_timesheet_corrections_scope_status",
        "timesheet_corrections",
        ["organization_id", "status"],
    )
    op.create_index(
        "ix_timesheet_corrections_period", "timesheet_corrections", ["timesheet_period_id"]
    )
    op.create_index(
        "ix_timesheet_corrections_process_instance",
        "timesheet_corrections",
        ["process_instance_id"],
    )


def downgrade() -> None:
    op.drop_table("timesheet_corrections")
    op.drop_table("timesheet_entries")
    op.drop_table("timesheet_periods")
    op.drop_table("leave_balance_entries")
    op.drop_table("leave_requests")
    op.drop_table("employee_work_schedules")
    op.drop_table("work_schedule_days")
    op.drop_table("work_schedules")
    op.drop_table("leave_entitlements")
    op.drop_table("leave_types")
    op.drop_table("time_codes")
