import type { Correspondence, DashboardSnapshot, Employee, IncomingLetterInput, ProcessDefinition, WorkTask } from '../shared/types';

export interface CorrespondenceRepository {
  listIncoming(): Promise<Correspondence[]>;
  getIncoming(id: string): Promise<Correspondence>;
  checkDuplicate(sender: string, senderNumber: string): Promise<Correspondence | null>;
  registerIncoming(input: IncomingLetterInput): Promise<Correspondence>;
  sendForResolution(id: string): Promise<Correspondence>;
}

export interface TaskRepository {
  list(): Promise<WorkTask[]>;
  claim(id: string): Promise<WorkTask>;
  complete(id: string): Promise<WorkTask>;
}

export interface WorkflowRepository {
  listDefinitions(): Promise<ProcessDefinition[]>;
  retryIncident(id: string): Promise<ProcessDefinition>;
}

export interface OrganizationRepository {
  listEmployees(): Promise<Employee[]>;
}

export interface OperationsRepository {
  dashboard(): Promise<DashboardSnapshot>;
  reset(): Promise<void>;
}
