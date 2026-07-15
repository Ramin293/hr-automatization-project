import { ADD_EMPLOYEE_DRAFT_KEY, type AddEmployeeFormValues } from './schema';

export type EmployeeDraft = { values: AddEmployeeFormValues; savedAt: string };

export function saveEmployeeDraft(storage: Storage, values: AddEmployeeFormValues, now = new Date()) {
  const draft: EmployeeDraft = { values, savedAt: now.toISOString() };
  storage.setItem(ADD_EMPLOYEE_DRAFT_KEY, JSON.stringify(draft));
  return draft;
}

export function restoreEmployeeDraft(storage: Storage): EmployeeDraft | null {
  const raw = storage.getItem(ADD_EMPLOYEE_DRAFT_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as EmployeeDraft | AddEmployeeFormValues;
    if ('values' in parsed && 'savedAt' in parsed) return parsed;
    return { values: parsed, savedAt: new Date(0).toISOString() };
  } catch { return null; }
}

export function clearEmployeeDraft(storage: Storage) { storage.removeItem(ADD_EMPLOYEE_DRAFT_KEY); }
