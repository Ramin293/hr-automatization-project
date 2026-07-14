import { Inject, Injectable } from '@nestjs/common';
import { EmployeeStatus, LeaveRequestStatus } from '@prisma/client';
import { RequestContext } from '../auth/auth.types';
import { errors } from '../common/domain-error';
import { DOCUMENT_GATEWAY, DocumentGateway, WORKFLOW_GATEWAY, WorkflowGateway } from '../integrations/integration.ports';
import { CreateLeaveRequestDto, LeaveQueryDto, ReviewLeaveRequestDto } from './dto/leave.dto';
import { HR_REPOSITORY, HrRepository, LeaveRecord } from './hr.repository';

@Injectable()
export class LeaveService {
  constructor(
    @Inject(HR_REPOSITORY) private readonly repository: HrRepository,
    @Inject(DOCUMENT_GATEWAY) private readonly documents: DocumentGateway,
    @Inject(WORKFLOW_GATEWAY) private readonly workflows: WorkflowGateway
  ) {}

  list(query: LeaveQueryDto, context: RequestContext) {
    if (context.role === 'HR_SPECIALIST') return this.repository.listLeaveRequests(query);
    if (!context.employeeId) throw errors.forbidden();
    if (context.role === 'MANAGER') return this.repository.listLeaveRequests({ ...query, employeeId: undefined, managerId: context.employeeId });
    return this.repository.listLeaveRequests({ ...query, employeeId: context.employeeId });
  }

  async get(id: string, context: RequestContext) {
    const leave = await this.requireLeave(id);
    await this.assertCanRead(leave, context);
    return leave;
  }

  async create(dto: CreateLeaveRequestDto, idempotencyKey: string | undefined, context: RequestContext) {
    this.assertIdempotencyKey(idempotencyKey);
    if (context.role !== 'HR_SPECIALIST' && context.employeeId !== dto.employeeId) throw errors.forbidden('hr.leave.request');
    const existing = await this.repository.getLeaveByIdempotencyKey(idempotencyKey);
    if (existing) return existing;

    const startDate = new Date(dto.startDate);
    const endDate = new Date(dto.endDate);
    if (endDate < startDate) throw errors.validation('INVALID_LEAVE_PERIOD', 'Leave end date must not precede start date');
    if (startDate.getUTCFullYear() !== endDate.getUTCFullYear()) throw errors.validation('CROSS_YEAR_LEAVE_UNSUPPORTED', 'Split cross-year leave into separate requests');
    const duration = Math.floor((Date.UTC(endDate.getUTCFullYear(), endDate.getUTCMonth(), endDate.getUTCDate()) - Date.UTC(startDate.getUTCFullYear(), startDate.getUTCMonth(), startDate.getUTCDate())) / 86_400_000) + 1;
    if (duration > 60) throw errors.validation('LEAVE_DURATION_EXCEEDED', 'A single leave request cannot exceed 60 calendar days');
    if (dto.substituteEmployeeId === dto.employeeId) throw errors.validation('INVALID_SUBSTITUTE', 'Employee cannot substitute for themselves');

    const preparation = await this.repository.prepareLeave(dto.employeeId, dto.substituteEmployeeId, dto.leaveType, startDate, endDate);
    if (preparation.employee.status !== EmployeeStatus.ACTIVE) throw errors.conflict('EMPLOYEE_NOT_ACTIVE', 'Only active employees can request leave');
    if (!preparation.substituteExists) throw errors.validation('SUBSTITUTE_NOT_FOUND', 'Substitute employee was not found');
    if (preparation.overlap) throw errors.conflict('LEAVE_PERIOD_OVERLAP', 'Leave request overlaps an existing request');
    if (preparation.availableBalance < duration) throw errors.conflict('LEAVE_BALANCE_EXCEEDED', 'Available leave balance is insufficient', { available: preparation.availableBalance, requested: duration });

    const [document, workflow] = await Promise.all([
      this.documents.createLeaveRequestDocument({ employeeId: dto.employeeId, startDate: dto.startDate, endDate: dto.endDate, idempotencyKey, correlationId: context.correlationId }),
      this.workflows.startLeaveRequest({ leaveRequestBusinessKey: `leave:${idempotencyKey}`, employeeId: dto.employeeId, managerId: preparation.employee.managerId ?? undefined, correlationId: context.correlationId })
    ]);
    return this.repository.createLeave({ ...dto, startDate, endDate, requestedDuration: duration, idempotencyKey, document, workflow }, context);
  }

  async review(id: string, dto: ReviewLeaveRequestDto, context: RequestContext) {
    const current = await this.requireLeave(id);
    if (dto.stage === 'manager') {
      if (!context.permissions.includes('hr.leave.approve.manager') || !context.employeeId) throw errors.forbidden('hr.leave.approve.manager');
      const employee = await this.repository.getEmployee(current.employeeId);
      if (!employee || employee.managerId !== context.employeeId) {
        await this.repository.recordSecurityAudit('LeaveRequest', id, 'LeaveReviewAccessDenied', context, 'Manager is not assigned to this employee');
        throw errors.forbidden();
      }
      return this.repository.reviewLeave({ id, expectedStatus: LeaveRequestStatus.MANAGER_REVIEW, nextStatus: dto.decision === 'approve' ? LeaveRequestStatus.HR_REVIEW : LeaveRequestStatus.REJECTED, expectedVersion: dto.version, reason: dto.reason, eventType: dto.decision === 'approve' ? 'LeaveManagerApproved' : 'LeaveManagerRejected', deductBalance: false }, context);
    }
    if (!context.permissions.includes('hr.leave.approve.hr')) throw errors.forbidden('hr.leave.approve.hr');
    return this.repository.reviewLeave({ id, expectedStatus: LeaveRequestStatus.HR_REVIEW, nextStatus: dto.decision === 'approve' ? LeaveRequestStatus.APPROVED : LeaveRequestStatus.REJECTED, expectedVersion: dto.version, reason: dto.reason, eventType: dto.decision === 'approve' ? 'LeaveHrApproved' : 'LeaveHrRejected', deductBalance: dto.decision === 'approve' }, context);
  }

  private async requireLeave(id: string) {
    const leave = await this.repository.getLeaveRequest(id);
    if (!leave) throw errors.notFound('leave_request');
    return leave;
  }

  private async assertCanRead(leave: LeaveRecord, context: RequestContext) {
    if (context.role === 'HR_SPECIALIST' || context.employeeId === leave.employeeId) return;
    if (context.role === 'MANAGER' && context.employeeId) {
      const employee = await this.repository.getEmployee(leave.employeeId);
      if (employee?.managerId === context.employeeId) return;
    }
    await this.repository.recordSecurityAudit('LeaveRequest', leave.id, 'LeaveAccessDenied', context, 'ABAC policy denied leave request access');
    throw errors.forbidden();
  }

  private assertIdempotencyKey(value?: string): asserts value is string {
    if (!value || value.length < 8 || value.length > 100 || !/^[A-Za-z0-9._:-]+$/.test(value)) {
      throw errors.validation('INVALID_IDEMPOTENCY_KEY', 'Idempotency-Key must contain 8-100 safe characters');
    }
  }
}
