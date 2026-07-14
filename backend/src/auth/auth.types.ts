export type Role = 'HR_SPECIALIST' | 'EMPLOYEE' | 'MANAGER' | 'PROCESS_ADMIN';

export type Permission =
  | 'hr.read'
  | 'hr.employee.read.self'
  | 'hr.employee.read.team'
  | 'hr.employee.read.all'
  | 'hr.employee.write'
  | 'hr.compensation.read'
  | 'hr.leave.request'
  | 'hr.leave.approve.manager'
  | 'hr.leave.approve.hr';

export interface RequestContext {
  userId: string;
  employeeId?: string;
  role: Role;
  departmentId?: string;
  permissions: Permission[];
  correlationId: string;
}

export const permissionsByRole: Record<Role, Permission[]> = {
  HR_SPECIALIST: ['hr.read', 'hr.employee.read.all', 'hr.employee.write', 'hr.compensation.read', 'hr.leave.request', 'hr.leave.approve.hr'],
  EMPLOYEE: ['hr.read', 'hr.employee.read.self', 'hr.leave.request'],
  MANAGER: ['hr.read', 'hr.employee.read.self', 'hr.employee.read.team', 'hr.leave.request', 'hr.leave.approve.manager'],
  PROCESS_ADMIN: ['hr.read']
};
