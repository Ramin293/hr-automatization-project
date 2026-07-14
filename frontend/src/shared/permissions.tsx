import type { PropsWithChildren } from 'react';
import { useDeveloperStore } from './store';
import type { PersonaId } from './types';

export type Permission =
  | 'correspondence.read' | 'correspondence.create' | 'correspondence.register' | 'correspondence.resolve'
  | 'task.read' | 'task.claim' | 'task.complete' | 'workflow.read' | 'workflow.definition.edit'
  | 'organization.read' | 'audit.read' | 'analytics.read' | 'admin.manage';

const matrix: Record<PersonaId, Permission[]> = {
  secretary: ['correspondence.read', 'correspondence.create', 'correspondence.register', 'task.read', 'task.claim', 'task.complete', 'workflow.read', 'organization.read', 'audit.read'],
  executive: ['correspondence.read', 'correspondence.resolve', 'task.read', 'task.claim', 'task.complete', 'workflow.read', 'organization.read', 'audit.read', 'analytics.read'],
  employee: ['correspondence.read', 'correspondence.create', 'task.read', 'task.claim', 'task.complete', 'workflow.read', 'organization.read'],
  'process-designer': ['correspondence.read', 'task.read', 'workflow.read', 'workflow.definition.edit', 'organization.read', 'audit.read', 'analytics.read', 'admin.manage']
};

export function usePermission(permission: Permission) {
  const persona = useDeveloperStore((state) => state.persona);
  return matrix[persona].includes(permission);
}

export function PermissionGate({ permission, children, fallback = null }: PropsWithChildren<{ permission: Permission; fallback?: React.ReactNode }>) {
  return usePermission(permission) ? children : fallback;
}

export function getPermissions(persona: PersonaId) { return matrix[persona]; }
