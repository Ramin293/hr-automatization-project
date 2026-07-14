import { EmployeeService } from './employee.service';
import { employeeFixture, repositoryMock } from './test-fixtures';

describe('EmployeeService', () => {
  it('removes compensation for an employee reading their own profile', async () => {
    const repository = repositoryMock();
    repository.getEmployee.mockResolvedValue(employeeFixture);
    const service = new EmployeeService(repository);
    const result = await service.get(employeeFixture.id, {
      userId: 'user-11', employeeId: employeeFixture.id, role: 'EMPLOYEE', departmentId: employeeFixture.departmentId,
      permissions: ['hr.read', 'hr.employee.read.self', 'hr.leave.request'], correlationId: 'correlation-test'
    });
    expect(result).not.toHaveProperty('salary');
    expect(result).not.toHaveProperty('currency');
  });

  it('audits a denied profile read', async () => {
    const repository = repositoryMock();
    repository.getEmployee.mockResolvedValue(employeeFixture);
    const service = new EmployeeService(repository);
    const context = { userId: 'user-99', employeeId: '00000000-0000-4000-8000-000000000099', role: 'EMPLOYEE' as const, permissions: ['hr.read' as const, 'hr.employee.read.self' as const], correlationId: 'correlation-test' };
    await expect(service.get(employeeFixture.id, context)).rejects.toMatchObject({ code: 'ACCESS_DENIED', status: 403 });
    expect(repository.recordSecurityAudit).toHaveBeenCalledWith('Employee', employeeFixture.id, 'EmployeeAccessDenied', context, expect.any(String));
  });
});
