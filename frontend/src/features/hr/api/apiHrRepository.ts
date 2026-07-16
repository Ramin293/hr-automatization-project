import { ApiClient } from '../../../repositories/apiRepositories';
import type {
  CoreEmployeeRecord,
  CreateLeaveRequestInput,
  EmployeeFunctionDescriptor,
  HrEmployee,
  HrOverview,
  LeaveRequest,
  StaffingSlotOption
} from '../model/types';
import type { HrRepository } from './contracts';

type StructureUnit = { id: string; name: string };
type StructureNode = { unit: StructureUnit; children: StructureNode[] };
type StructureView = {
  root: StructureNode | null;
  staffingSlots: Array<{ id: string; organizationUnitId: string; positionDefinitionId: string; status: string }>;
};
type PositionDefinition = { id: string; name: string };

function flattenUnits(node: StructureNode | null, into: Map<string, string>) {
  if (!node) return into;
  into.set(node.unit.id, node.unit.name);
  node.children.forEach((child) => flattenUnits(child, into));
  return into;
}

export class ApiHrRepository implements HrRepository {
  constructor(private readonly api = new ApiClient()) {}

  getOverview() { return this.api.get<HrOverview>('/hr/overview'); }
  listEmployees() { return this.api.get<HrEmployee[]>('/hr/employees'); }
  getEmployee(id: string) { return this.api.get<HrEmployee>(`/hr/employees/${id}`); }
  getCurrentEmployee() { return this.api.get<HrEmployee>('/hr/employees/me'); }
  listCollectionFunctions() { return this.api.get<EmployeeFunctionDescriptor[]>('/employees/functions'); }
  listEmployeeFunctions(employeeId: string) { return this.api.get<EmployeeFunctionDescriptor[]>(`/employees/${employeeId}/functions`); }
  invokeEmployeeFunction(employeeId: string, key: string, payload: Record<string, unknown>) {
    return this.api.post<unknown>(`/employees/${employeeId}/functions/${key}`, { payload });
  }
  getCoreEmployee(employeeId: string) { return this.api.get<CoreEmployeeRecord>(`/employees/${employeeId}`); }
  async listVacantSlots(): Promise<StaffingSlotOption[]> {
    const [structure, positions] = await Promise.all([
      this.api.get<StructureView>('/organization/structure/active'),
      this.api.get<PositionDefinition[]>('/positions?pageSize=100')
    ]);
    const unitNames = flattenUnits(structure.root, new Map<string, string>());
    const positionNames = new Map(positions.map((item) => [item.id, item.name]));
    return structure.staffingSlots
      .filter((slot) => slot.status === 'vacant' || slot.status === 'approved')
      .map((slot) => ({
        id: slot.id,
        label: [
          positionNames.get(slot.positionDefinitionId) ?? 'Должность',
          unitNames.get(slot.organizationUnitId) ?? 'Подразделение'
        ].join(' · ')
      }))
      .sort((left, right) => left.label.localeCompare(right.label, 'ru'));
  }
  listLeaveRequests() { return this.api.get<LeaveRequest[]>('/hr/leave-requests'); }
  createLeaveRequest(input: CreateLeaveRequestInput) { return this.api.post<LeaveRequest>('/hr/leave-requests', input); }
  reviewLeaveRequest(id: string, decision: 'approve' | 'reject') {
    return this.api.post<LeaveRequest>(`/hr/leave-requests/${id}/review`, { decision, reason: decision === 'reject' ? 'Returned for correction by the reviewer' : '' });
  }
  submitHiringRequest(values: Record<string, unknown>, attachments: Array<{ name: string; size: number; category: string }>) {
    return this.api.post<{ id: string; number: string; status: string; currentStep: string }>('/hr/hiring/requests', { values, attachments });
  }
  async reset() { /* Server records and audit history are intentionally immutable. */ }
}
