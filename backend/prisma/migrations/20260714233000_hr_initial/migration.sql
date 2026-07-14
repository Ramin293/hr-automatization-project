-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "EmployeeStatus" AS ENUM ('DRAFT', 'PRE_HIRE', 'ACTIVE', 'ON_LEAVE', 'SICK_LEAVE', 'LONG_TERM_LEAVE', 'SUSPENDED', 'TERMINATION_PENDING', 'TERMINATED', 'ARCHIVED');

-- CreateEnum
CREATE TYPE "Availability" AS ENUM ('AVAILABLE', 'AWAY', 'REMOTE');

-- CreateEnum
CREATE TYPE "StaffingStatus" AS ENUM ('VACANT', 'OCCUPIED', 'FROZEN', 'CLOSED');

-- CreateEnum
CREATE TYPE "LeaveRequestStatus" AS ENUM ('DRAFT', 'SUBMITTED', 'MANAGER_REVIEW', 'HR_REVIEW', 'APPROVED', 'REJECTED', 'RETURNED_FOR_REVISION', 'CANCELLED', 'IN_PROGRESS', 'COMPLETED');

-- CreateEnum
CREATE TYPE "OutboxStatus" AS ENUM ('PENDING', 'PUBLISHED', 'FAILED');

-- CreateTable
CREATE TABLE "hr_departments" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "hr_departments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_positions" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "hr_positions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_staffing_positions" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "department_id" UUID NOT NULL,
    "position_id" UUID NOT NULL,
    "status" "StaffingStatus" NOT NULL DEFAULT 'VACANT',
    "fte" DECIMAL(4,2) NOT NULL DEFAULT 1,
    "valid_from" DATE NOT NULL,
    "valid_to" DATE,
    "salary_min" DECIMAL(14,2),
    "salary_max" DECIMAL(14,2),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT "hr_staffing_positions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_employees" (
    "id" UUID NOT NULL,
    "employee_number" TEXT NOT NULL,
    "status" "EmployeeStatus" NOT NULL DEFAULT 'DRAFT',
    "availability" "Availability" NOT NULL DEFAULT 'AVAILABLE',
    "full_name" TEXT NOT NULL,
    "initials" TEXT NOT NULL,
    "work_email" TEXT NOT NULL,
    "work_phone" TEXT NOT NULL,
    "department_id" UUID NOT NULL,
    "position_id" UUID NOT NULL,
    "staffing_position_id" UUID,
    "manager_id" UUID,
    "legal_entity_id" TEXT NOT NULL,
    "location_id" TEXT NOT NULL,
    "employment_type" TEXT NOT NULL,
    "fte" DECIMAL(4,2) NOT NULL DEFAULT 1,
    "work_schedule_id" TEXT NOT NULL,
    "start_date" DATE NOT NULL,
    "contract_end_date" DATE,
    "probation_start_date" DATE,
    "probation_end_date" DATE,
    "personnel_file_completeness" INTEGER NOT NULL DEFAULT 0,
    "salary" DECIMAL(14,2),
    "currency" TEXT NOT NULL DEFAULT 'KZT',
    "candidate_groups" TEXT[],
    "skills" TEXT[],
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "created_by" TEXT NOT NULL,
    "updated_by" TEXT NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT "hr_employees_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_leave_balances" (
    "id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "leave_type" TEXT NOT NULL,
    "year" INTEGER NOT NULL,
    "available" DECIMAL(8,2) NOT NULL,
    "reserved" DECIMAL(8,2) NOT NULL DEFAULT 0,
    "used" DECIMAL(8,2) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT "hr_leave_balances_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_leave_requests" (
    "id" UUID NOT NULL,
    "employee_id" UUID NOT NULL,
    "leave_type" TEXT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "requested_duration" DECIMAL(8,2) NOT NULL,
    "half_day" BOOLEAN NOT NULL DEFAULT false,
    "custom_hours" DECIMAL(5,2),
    "substitute_employee_id" UUID,
    "comment" TEXT,
    "contact_during_leave" TEXT,
    "balance_snapshot" DECIMAL(8,2) NOT NULL,
    "status" "LeaveRequestStatus" NOT NULL DEFAULT 'SUBMITTED',
    "document_id" TEXT,
    "document_number" TEXT,
    "workflow_instance_id" TEXT,
    "workflow_step" TEXT,
    "audit_correlation_id" TEXT NOT NULL,
    "idempotency_key" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "created_by" TEXT NOT NULL,
    "updated_by" TEXT NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT "hr_leave_requests_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_audit_events" (
    "id" UUID NOT NULL,
    "aggregate_type" TEXT NOT NULL,
    "aggregate_id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "actor_id" TEXT NOT NULL,
    "actor_role" TEXT NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "workflow_instance_id" TEXT,
    "reason" TEXT,
    "changes" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "hr_audit_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "hr_outbox_events" (
    "id" UUID NOT NULL,
    "event_type" TEXT NOT NULL,
    "aggregate_type" TEXT NOT NULL,
    "aggregate_id" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "status" "OutboxStatus" NOT NULL DEFAULT 'PENDING',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "published_at" TIMESTAMP(3),

    CONSTRAINT "hr_outbox_events_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "hr_departments_code_key" ON "hr_departments"("code");

-- CreateIndex
CREATE UNIQUE INDEX "hr_positions_code_key" ON "hr_positions"("code");

-- CreateIndex
CREATE UNIQUE INDEX "hr_staffing_positions_code_key" ON "hr_staffing_positions"("code");

-- CreateIndex
CREATE INDEX "hr_staffing_positions_department_id_status_idx" ON "hr_staffing_positions"("department_id", "status");

-- CreateIndex
CREATE UNIQUE INDEX "hr_employees_employee_number_key" ON "hr_employees"("employee_number");

-- CreateIndex
CREATE UNIQUE INDEX "hr_employees_work_email_key" ON "hr_employees"("work_email");

-- CreateIndex
CREATE UNIQUE INDEX "hr_employees_staffing_position_id_key" ON "hr_employees"("staffing_position_id");

-- CreateIndex
CREATE INDEX "hr_employees_department_id_idx" ON "hr_employees"("department_id");

-- CreateIndex
CREATE INDEX "hr_employees_manager_id_idx" ON "hr_employees"("manager_id");

-- CreateIndex
CREATE INDEX "hr_employees_staffing_position_id_idx" ON "hr_employees"("staffing_position_id");

-- CreateIndex
CREATE INDEX "hr_employees_status_idx" ON "hr_employees"("status");

-- CreateIndex
CREATE INDEX "hr_leave_balances_employee_id_idx" ON "hr_leave_balances"("employee_id");

-- CreateIndex
CREATE UNIQUE INDEX "hr_leave_balances_employee_id_leave_type_year_key" ON "hr_leave_balances"("employee_id", "leave_type", "year");

-- CreateIndex
CREATE UNIQUE INDEX "hr_leave_requests_idempotency_key_key" ON "hr_leave_requests"("idempotency_key");

-- CreateIndex
CREATE INDEX "hr_leave_requests_employee_id_start_date_end_date_idx" ON "hr_leave_requests"("employee_id", "start_date", "end_date");

-- CreateIndex
CREATE INDEX "hr_leave_requests_status_idx" ON "hr_leave_requests"("status");

-- CreateIndex
CREATE INDEX "hr_leave_requests_workflow_instance_id_idx" ON "hr_leave_requests"("workflow_instance_id");

-- CreateIndex
CREATE INDEX "hr_leave_requests_document_id_idx" ON "hr_leave_requests"("document_id");

-- CreateIndex
CREATE INDEX "hr_audit_events_aggregate_type_aggregate_id_idx" ON "hr_audit_events"("aggregate_type", "aggregate_id");

-- CreateIndex
CREATE INDEX "hr_audit_events_correlation_id_idx" ON "hr_audit_events"("correlation_id");

-- CreateIndex
CREATE INDEX "hr_outbox_events_status_created_at_idx" ON "hr_outbox_events"("status", "created_at");

-- AddForeignKey
ALTER TABLE "hr_staffing_positions" ADD CONSTRAINT "hr_staffing_positions_department_id_fkey" FOREIGN KEY ("department_id") REFERENCES "hr_departments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_staffing_positions" ADD CONSTRAINT "hr_staffing_positions_position_id_fkey" FOREIGN KEY ("position_id") REFERENCES "hr_positions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_employees" ADD CONSTRAINT "hr_employees_department_id_fkey" FOREIGN KEY ("department_id") REFERENCES "hr_departments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_employees" ADD CONSTRAINT "hr_employees_position_id_fkey" FOREIGN KEY ("position_id") REFERENCES "hr_positions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_employees" ADD CONSTRAINT "hr_employees_staffing_position_id_fkey" FOREIGN KEY ("staffing_position_id") REFERENCES "hr_staffing_positions"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_employees" ADD CONSTRAINT "hr_employees_manager_id_fkey" FOREIGN KEY ("manager_id") REFERENCES "hr_employees"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_leave_balances" ADD CONSTRAINT "hr_leave_balances_employee_id_fkey" FOREIGN KEY ("employee_id") REFERENCES "hr_employees"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_leave_requests" ADD CONSTRAINT "hr_leave_requests_employee_id_fkey" FOREIGN KEY ("employee_id") REFERENCES "hr_employees"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "hr_leave_requests" ADD CONSTRAINT "hr_leave_requests_substitute_employee_id_fkey" FOREIGN KEY ("substitute_employee_id") REFERENCES "hr_employees"("id") ON DELETE SET NULL ON UPDATE CASCADE;
