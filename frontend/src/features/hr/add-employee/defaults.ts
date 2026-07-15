import { currencies, educationLevels, employmentTypes, executives, hiringReasons, workArrangements, workSchedules } from './referenceData';
import type { AddEmployeeFormValues } from './schema';
import { buildRequestText } from './utils';

export const addEmployeeDefaults: AddEmployeeFormValues = {
  recipient: executives[0].name, recipientPosition: executives[0].position, recipientDepartment: executives[0].department, recipientType: executives[0].type, requestDate: new Date().toISOString().slice(0, 10),
  initiatorName: 'Зарина Ахметова', initiatorPosition: 'HR специалист', initiatorDepartment: 'Департамент управления персоналом', initiatorEmail: 'z.akhmetova@ertis.kz', initiatorPhone: '+7 7182 55 10 10',
  lastName: '', firstName: '', middleName: '', iin: '', birthDate: '', gender: '', citizenship: 'Республика Казахстан', personalPhone: '', personalEmail: '', address: '', maritalStatus: '', emergencyContact: '', emergencyPhone: '', identityDocumentType: 'Удостоверение личности', identityDocumentNumber: '', identityIssueDate: '', identityExpirationDate: '', issuingAuthority: '',
  department: '', team: '', position: '', manager: '', employmentType: employmentTypes[0], workArrangement: workArrangements[0], workplace: 'Павлодар', startDate: '', probationMonths: 3, schedule: workSchedules[0], fte: 1, salary: '', currency: currencies[0], hiringReason: hiringReasons[1], responsibilities: '', justification: '',
  educationLevel: educationLevels[2], institution: '', specialization: '', graduationYear: '', qualification: '', totalExperience: '', relevantExperience: '', skills: '', languages: '', certifications: '', additionalInfo: '', requestText: buildRequestText({ lastName: '', firstName: '', middleName: '', position: '', department: '', startDate: '', hiringReason: hiringReasons[1] })
};
