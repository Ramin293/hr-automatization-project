import type { AddEmployeeFormValues } from './schema';
import type { AttachmentCategory } from './referenceData';

export type EmployeeAttachment = { id: string; category: AttachmentCategory; file: File };
export const MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024;
export const SUPPORTED_ATTACHMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'];

export const buildEmployeeFullName = (values: Pick<AddEmployeeFormValues, 'lastName' | 'firstName' | 'middleName'>) => [values.lastName, values.firstName, values.middleName].map((part) => part.trim()).filter(Boolean).join(' ');

export const buildRequestText = (values: Pick<AddEmployeeFormValues, 'lastName' | 'firstName' | 'middleName' | 'position' | 'department' | 'startDate' | 'hiringReason'>) => {
  const fullName = buildEmployeeFullName(values) || '[ФИО сотрудника]';
  return `Прошу рассмотреть возможность приёма ${fullName} на должность ${values.position || '[должность]'} в ${values.department || '[подразделение]'} с предполагаемой датой выхода ${values.startDate || '[дата]'}. Основание: ${values.hiringReason || '[основание]'}.`;
};

export const createEmployeeRequestFilename = (values: Pick<AddEmployeeFormValues, 'lastName' | 'firstName' | 'requestDate'>) => {
  const safe = `${values.lastName}_${values.firstName}`.trim().replace(/[^\p{L}\p{N}_-]+/gu, '_');
  return `Employee_Hiring_Request_${safe}_${values.requestDate}.docx`;
};

export function validateAttachment(file: File) {
  const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
  if (!SUPPORTED_ATTACHMENT_EXTENSIONS.includes(extension)) return 'Допустимы PDF, DOC, DOCX, JPG и PNG';
  if (file.size > MAX_ATTACHMENT_SIZE) return 'Размер файла не должен превышать 10 МБ';
  return null;
}

export function buildAttachmentList(attachments: EmployeeAttachment[]) {
  const counts = new Map<AttachmentCategory, number>();
  attachments.forEach(({ category }) => counts.set(category, (counts.get(category) ?? 0) + 1));
  return [...counts].map(([category, count], index) => `${index + 1}. ${category} — ${count} ${count === 1 ? 'файл' : 'файла'}`);
}
