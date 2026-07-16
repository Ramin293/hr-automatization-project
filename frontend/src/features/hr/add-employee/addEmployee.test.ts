import { beforeEach, describe, expect, it } from 'vitest';
import { clearEmployeeDraft, restoreEmployeeDraft, saveEmployeeDraft } from './draft';
import { addEmployeeDefaults } from './defaults';
import { addEmployeeSchema } from './schema';
import { buildAttachmentList, buildEmployeeFullName, buildRequestText, createEmployeeRequestFilename, validateAttachment, type EmployeeAttachment } from './utils';

const validValues = () => ({
  ...addEmployeeDefaults, lastName: 'Садыкова', firstName: 'Алия', middleName: 'Ерлановна', iin: '900101300001', birthDate: '1990-01-01', gender: 'Женский', personalPhone: '+7 700 000 00 00', personalEmail: 'aliya@example.com', address: 'Павлодар', maritalStatus: 'Не состоит в браке', identityDocumentNumber: '012345678', department: 'Департамент управления персоналом', position: 'HR специалист', manager: 'Сауле Бекенова', startDate: '2026-08-01', responsibilities: 'Кадровое администрирование', justification: 'Усиление команды', institution: 'Торайгыров университет', specialization: 'Управление персоналом', totalExperience: '3 года'
});

describe('Add Employee frontend domain', () => {
  beforeEach(() => localStorage.clear());

  it('validates a complete form and rejects invalid IIN and dates', () => {
    expect(addEmployeeSchema.safeParse(validValues()).success).toBe(true);
    const invalid = addEmployeeSchema.safeParse({ ...validValues(), iin: '123', birthDate: '2999-01-01', identityIssueDate: '2026-01-02', identityExpirationDate: '2026-01-01' });
    expect(invalid.success).toBe(false);
    if (!invalid.success) expect(invalid.error.issues.map((issue) => issue.path[0])).toEqual(expect.arrayContaining(['iin', 'birthDate', 'identityExpirationDate']));
  });

  it('builds full name, request text and deterministic DOCX filename', () => {
    const values = validValues();
    expect(buildEmployeeFullName(values)).toBe('Садыкова Алия Ерлановна');
    expect(buildRequestText(values)).toContain('Садыкова Алия Ерлановна');
    expect(buildRequestText(values)).toContain('HR специалист');
    expect(createEmployeeRequestFilename(values)).toBe(`Employee_Hiring_Request_Садыкова_Алия_${values.requestDate}.docx`);
  });

  it('validates and groups local attachments', () => {
    expect(validateAttachment(new File(['ok'], 'diploma.pdf'))).toBeNull();
    expect(validateAttachment(new File(['bad'], 'script.exe'))).toContain('Допустимы');
    const attachments = [
      { id: '1', category: 'Диплом', file: new File(['a'], 'one.pdf') },
      { id: '2', category: 'Диплом', file: new File(['b'], 'two.pdf') },
      { id: '3', category: 'Резюме', file: new File(['c'], 'resume.docx') }
    ] satisfies EmployeeAttachment[];
    expect(buildAttachmentList(attachments)).toEqual(['1. Диплом — 2 файла', '2. Резюме — 1 файл']);
  });

  it('saves, restores and clears the browser draft', () => {
    const values = validValues();
    saveEmployeeDraft(localStorage, values, new Date('2026-07-15T10:00:00.000Z'));
    expect(restoreEmployeeDraft(localStorage)).toEqual({ values, savedAt: '2026-07-15T10:00:00.000Z' });
    clearEmployeeDraft(localStorage);
    expect(restoreEmployeeDraft(localStorage)).toBeNull();
  });
});
