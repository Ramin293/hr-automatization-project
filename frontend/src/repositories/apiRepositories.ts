import type { CorrespondenceRepository, OperationsRepository, OrganizationRepository, TaskRepository, WorkflowRepository } from './contracts';

export type ApiRepositories = CorrespondenceRepository & TaskRepository & WorkflowRepository & OrganizationRepository & OperationsRepository;

export class ApiAdapterBoundary {
  constructor(readonly baseUrl: string) {}

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } });
    if (!response.ok) throw new Error(`API_${response.status}`);
    return response.json() as Promise<T>;
  }
}
