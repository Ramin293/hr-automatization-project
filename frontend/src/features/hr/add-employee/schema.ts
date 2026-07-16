import { z } from 'zod';

const required = (message: string) => z.string().trim().min(1, message);
const phone = z.string().trim().regex(/^\+?[0-9 ()-]{7,20}$/, 'Некорректный номер телефона');
const optionalPhone = z.string().trim().refine((value) => !value || /^\+?[0-9 ()-]{7,20}$/.test(value), 'Некорректный номер телефона');
const optionalNonNegative = z.string().trim().refine((value) => !value || (Number.isFinite(Number(value)) && Number(value) >= 0), 'Значение не может быть отрицательным');

export const addEmployeeSchema = z.object({
  recipient: required('Выберите получателя'), recipientPosition: required('Укажите должность получателя'), recipientDepartment: required('Укажите подразделение получателя'), recipientType: required('Выберите тип получателя'), requestDate: required('Укажите дату обращения'),
  initiatorName: required('Укажите инициатора'), initiatorPosition: required('Укажите должность инициатора'), initiatorDepartment: required('Укажите подразделение инициатора'), initiatorEmail: z.string().email('Некорректный рабочий e-mail'), initiatorPhone: phone,
  lastName: required('Укажите фамилию'), firstName: required('Укажите имя'), middleName: z.string(), iin: z.string().regex(/^\d{12}$/, 'ИИН должен содержать 12 цифр'), birthDate: required('Укажите дату рождения'), gender: required('Выберите пол'), citizenship: required('Укажите гражданство'), personalPhone: phone, personalEmail: z.string().email('Некорректный личный e-mail'), address: required('Укажите адрес проживания'),
  maritalStatus: required('Выберите семейное положение'), emergencyContact: z.string(), emergencyPhone: optionalPhone, identityDocumentType: required('Выберите тип документа'), identityDocumentNumber: required('Укажите номер документа'), identityIssueDate: z.string(), identityExpirationDate: z.string(), issuingAuthority: z.string(),
  department: required('Выберите подразделение'), team: z.string(), position: required('Выберите предлагаемую должность'), manager: required('Выберите непосредственного руководителя'), employmentType: required('Выберите вид занятости'), workArrangement: required('Выберите формат работы'), workplace: required('Укажите место работы'), startDate: required('Укажите дату выхода'), probationMonths: z.number().min(0, 'Срок не может быть отрицательным').max(6, 'Максимальный срок — 6 месяцев'), schedule: required('Выберите график'), fte: z.number().min(0.1).max(1), salary: optionalNonNegative, currency: required('Выберите валюту'), hiringReason: required('Выберите основание'), responsibilities: required('Опишите обязанности'), justification: required('Добавьте деловое обоснование'),
  educationLevel: required('Выберите уровень образования'), institution: required('Укажите учебное заведение'), specialization: required('Укажите специальность'), graduationYear: z.string(), qualification: z.string(), totalExperience: required('Укажите опыт работы'), relevantExperience: z.string(), skills: z.string(), languages: z.string(), certifications: z.string(), additionalInfo: z.string(), requestText: required('Введите текст служебной записки')
}).superRefine((values, context) => {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  if (values.birthDate && new Date(values.birthDate) >= today) context.addIssue({ code: 'custom', path: ['birthDate'], message: 'Дата рождения должна быть в прошлом' });
  const oldestStart = new Date(today); oldestStart.setFullYear(oldestStart.getFullYear() - 1);
  if (values.startDate && new Date(values.startDate) < oldestStart) context.addIssue({ code: 'custom', path: ['startDate'], message: 'Дата выхода не может быть более года в прошлом' });
  if (values.identityIssueDate && values.identityExpirationDate && new Date(values.identityExpirationDate) <= new Date(values.identityIssueDate)) context.addIssue({ code: 'custom', path: ['identityExpirationDate'], message: 'Срок действия должен быть позже даты выдачи' });
});

export type AddEmployeeFormValues = z.infer<typeof addEmployeeSchema>;
export const ADD_EMPLOYEE_DRAFT_KEY = 'ertis.hr.add-employee.draft.v1';
