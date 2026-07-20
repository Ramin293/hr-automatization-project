import { Section } from '../../../shared/components';
import { ReferenceTable } from '../components';
import { ProcessSystemPage } from '../ProcessSystemPage';
import { LEAVE_DOCUMENTS, LEAVE_GATES, LEAVE_META, LEAVE_PAYMENT, LEAVE_PLANNING, LEAVE_ROLES, LEAVE_STAGES, LEAVE_STATUSES, LEAVE_TYPES } from '../data/leave';

export default function LeaveSystemPage() {
  return (
    <ProcessSystemPage
      config={{
        meta: LEAVE_META,
        stages: LEAVE_STAGES,
        roles: LEAVE_ROLES,
        gates: LEAVE_GATES,
        statuses: LEAVE_STATUSES,
        documents: LEAVE_DOCUMENTS,
        extraTabs: [
          {
            id: 'types',
            label: 'Виды отпуска',
            count: LEAVE_TYPES.length,
            render: () => (
              <Section title="Справочник видов отпуска" meta="L01–L16 · выбор кода без свободного текста">
                <ReferenceTable
                  rows={LEAVE_TYPES}
                  columns={[
                    { key: 'code', label: 'Код' },
                    { key: 'title', label: 'Вид' },
                    { key: 'basis', label: 'Основание' },
                    { key: 'mode', label: 'Режим' }
                  ]}
                />
              </Section>
            )
          },
          {
            id: 'planning',
            label: 'Планирование',
            count: LEAVE_PLANNING.length,
            render: () => (
              <Section title="Годовое планирование отпусков" meta="От открытия цикла до графика">
                <ReferenceTable
                  rows={LEAVE_PLANNING.map((item) => ({ ...item, step: String(item.step) }))}
                  columns={[
                    { key: 'step', label: '№' },
                    { key: 'action', label: 'Действие' },
                    { key: 'owner', label: 'Владелец' },
                    { key: 'result', label: 'Результат' }
                  ]}
                />
              </Section>
            )
          },
          {
            id: 'payment',
            label: 'Оплата',
            count: LEAVE_PAYMENT.length,
            render: () => (
              <Section title="Расчёт, оплата и остатки" meta="Средний заработок по Приказу №908">
                <ReferenceTable
                  rows={LEAVE_PAYMENT}
                  columns={[
                    { key: 'type', label: 'Вид' },
                    { key: 'unit', label: 'Единица' },
                    { key: 'calc', label: 'Расчёт' },
                    { key: 'term', label: 'Срок' }
                  ]}
                />
              </Section>
            )
          }
        ]
      }}
    />
  );
}
