import { LeaveService } from './leave.service';
import { employeeFixture, leaveFixture, repositoryMock } from './test-fixtures';

describe('LeaveService', () => {
  const context = { userId: 'user-11', employeeId: employeeFixture.id, role: 'EMPLOYEE' as const, permissions: ['hr.read' as const, 'hr.employee.read.self' as const, 'hr.leave.request' as const], correlationId: 'correlation-test' };

  it('returns an existing result for a repeated idempotency key', async () => {
    const repository = repositoryMock();
    repository.getLeaveByIdempotencyKey.mockResolvedValue(leaveFixture);
    const documents = { createLeaveRequestDocument: jest.fn() };
    const workflows = { startLeaveRequest: jest.fn() };
    const service = new LeaveService(repository, documents, workflows);
    const result = await service.create({ employeeId: employeeFixture.id, leaveType: 'ANNUAL_PAID', startDate: '2026-09-01', endDate: '2026-09-03' }, 'request-0001', context);
    expect(result).toBe(leaveFixture);
    expect(documents.createLeaveRequestDocument).not.toHaveBeenCalled();
    expect(workflows.startLeaveRequest).not.toHaveBeenCalled();
  });

  it('rejects a request that exceeds the available balance', async () => {
    const repository = repositoryMock();
    repository.getLeaveByIdempotencyKey.mockResolvedValue(null);
    repository.prepareLeave.mockResolvedValue({ employee: { id: employeeFixture.id, status: employeeFixture.status, managerId: employeeFixture.managerId }, substituteExists: true, availableBalance: 1, overlap: false });
    const service = new LeaveService(repository, { createLeaveRequestDocument: jest.fn() }, { startLeaveRequest: jest.fn() });
    await expect(service.create({ employeeId: employeeFixture.id, leaveType: 'ANNUAL_PAID', startDate: '2026-09-01', endDate: '2026-09-03' }, 'request-0002', context)).rejects.toMatchObject({ code: 'LEAVE_BALANCE_EXCEEDED' });
  });
});
