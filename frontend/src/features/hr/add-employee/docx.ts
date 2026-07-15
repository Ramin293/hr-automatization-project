import { AlignmentType, Document, HeadingLevel, Packer, Paragraph, TextRun } from 'docx';
import type { AddEmployeeFormValues } from './schema';
import { buildAttachmentList, buildEmployeeFullName, type EmployeeAttachment } from './utils';

const line = (label: string, value: string | number) => new Paragraph({ spacing: { after: 90 }, children: [new TextRun({ text: `${label}: `, bold: true }), new TextRun(String(value || '—'))] });
const heading = (text: string) => new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });

export async function createAddEmployeeDocx(values: AddEmployeeFormValues, attachments: EmployeeAttachment[]) {
  const attachmentLines = buildAttachmentList(attachments);
  const document = new Document({
    styles: { default: { document: { run: { font: 'Arial', size: 22 }, paragraph: { spacing: { line: 276 } } } } },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
      children: [
        new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `Кому: ${values.recipient}\n${values.recipientPosition}\n${values.recipientDepartment}` })] }),
        new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 360 }, children: [new TextRun({ text: `От: ${values.initiatorName}\n${values.initiatorPosition}\n${values.initiatorDepartment}` })] }),
        new Paragraph({ text: 'СЛУЖЕБНАЯ ЗАПИСКА', heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER }),
        new Paragraph({ text: 'О рассмотрении вопроса о приёме сотрудника', heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { after: 280 } }),
        line('Дата', values.requestDate), new Paragraph({ text: values.requestText, spacing: { before: 180, after: 240 } }),
        heading('Сведения о будущем сотруднике'), line('ФИО', buildEmployeeFullName(values)), line('ИИН', values.iin), line('Дата рождения', values.birthDate), line('Контакты', `${values.personalPhone}; ${values.personalEmail}`), line('Гражданство', values.citizenship),
        heading('Предлагаемые условия'), line('Подразделение', `${values.department}${values.team ? ` / ${values.team}` : ''}`), line('Должность', values.position), line('Руководитель', values.manager), line('Дата выхода', values.startDate), line('Занятость', `${values.employmentType}, ${values.workArrangement}, ${values.fte} FTE`), line('Испытательный срок', `${values.probationMonths} мес.`),
        heading('Образование и квалификация'), line('Образование', `${values.educationLevel}, ${values.institution}`), line('Специальность', values.specialization), line('Квалификация', values.qualification), line('Опыт', `${values.totalExperience}; релевантный: ${values.relevantExperience}`), line('Навыки', values.skills),
        heading('Деловое обоснование'), new Paragraph({ text: values.justification, spacing: { after: 200 } }),
        heading('Приложения'), ...(attachmentLines.length ? attachmentLines.map((text) => new Paragraph({ text, numbering: undefined })) : [new Paragraph('Приложения отсутствуют')]),
        new Paragraph({ text: `\nИнициатор: ____________________ / ${values.initiatorName}\nДата: ____________________` }),
        new Paragraph({ text: '\nРезолюция руководства: ______________________________________________\n____________________________________________________________________' })
      ]
    }]
  });
  return Packer.toBlob(document);
}

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = fileName; document.body.appendChild(anchor); anchor.click(); anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}
