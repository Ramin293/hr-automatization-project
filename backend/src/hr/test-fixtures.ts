import { Availability, EmployeeStatus, LeaveRequestStatus } from '@prisma/client';
import { EmployeeRecord, HrRepository, LeaveRecord } from './hr.repository';

export const employeeFixture: EmployeeRecord = {
  id: '00000000-0000-4000-8000-000000000011', employeeNumber: 'EMP-00011', status: EmployeeStatus.ACTIVE,
  availability: Availability.AVAILABLE, fullName: 'Employee Eleven', initials: 'EE', workEmail: 'employee.11@ertis.local',
  workPhone: '+77010000011', departmentId: '00000000-0000-4000-8000-000000000001', departmentName: 'Human Resources',
  positionId: '00000000-0000-4000-8000-000000000001', positionName: 'Specialist', staffingPositionId: null,
  managerId: '00000000-0000-4000-8000-000000000001', managerName: 'Manager One', locationId: 'ASTANA-HQ',
  employmentType: 'FULL_TIME', startDate: new Date('2024-01-01'), contractEndDate: null, probationEndDate: null,
  personnelFileCompleteness: 100, salary: 500000, currency: 'KZT', leaveBalance: 28, candidateGroups: [], skills: [], version: 1
};

export const leaveFixture: LeaveRecord = {
  id: '00000000-0000-4000-8000-000000000021', employeeId: employeeFixture.id, employeeName: employeeFixture.fullName,
  leaveType: 'ANNUAL_PAID', startDate: new Date('2026-09-01'), endDate: new Date('2026-09-03'), requestedDuration: 3,
  substituteEmployeeId: null, substituteName: null, comment: null, status: LeaveRequestStatus.MANAGER_REVIEW,
  documentId: 'document-1', documentNumber: 'HR-LV-1', workflowInstanceId: 'workflow-1', workflowStep: 'MANAGER_REVIEW',
  createdAt: new Date('2026-07-14'), version: 1
};

export const repositoryMock = (): jest.Mocked<HrRepository> => ({
  listEmployees: jest.fn(), getEmployee: jest.fn(), createEmployee: jest.fn(), getOverview: jest.fn(),
  listLeaveRequests: jest.fn(), getLeaveRequest: jest.fn(), getLeaveByIdempotencyKey: jest.fn(), prepareLeave: jest.fn(),
  createLeave: jest.fn(), reviewLeave: jest.fn(), recordSecurityAudit: jest.fn()
});
