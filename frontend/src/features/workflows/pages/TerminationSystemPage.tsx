import { Section } from '../../../shared/components';
import { ReferenceTable } from '../components';
import { ProcessSystemPage } from '../ProcessSystemPage';
import {
  TERMINATION_DOCUMENTS,
  TERMINATION_GATES,
  TERMINATION_GROUNDS,
  TERMINATION_META,
  TERMINATION_ROLES,
  TERMINATION_ROUTES,
  TERMINATION_SETTLEMENT,
  TERMINATION_STAGES,
  TERMINATION_STATUSES
} from '../data/termination';

export default function TerminationSystemPage() {
  return (
    <ProcessSystemPage
      config={{
        meta: TERMINATION_META,
        stages: TERMINATION_STAGES,
        roles: TERMINATION_ROLES,
        gates: TERMINATION_GATES,
        statuses: TERMINATION_STATUSES,
        documents: TERMINATION_DOCUMENTS,
        extraTabs: [
          {
            id: 'routes',
            label: 'Маршруты R1–R9',
            count: TERMINATION_ROUTES.length,
            render: () => (
              <Section title="Справочник юридических маршрутов" meta="Основания прекращения по ТК РК">
                <ReferenceTable
                  rows={TERMINATION_ROUTES}
                  columns={[
                    { key: 'code', label: 'Код' },
                    { key: 'route', label: 'Маршрут' },
                    { key: 'basis', label: 'Основание' },
                    { key: 'minPackage', label: 'Минимальный пакет' }
                  ]}
                />
              </Section>
            )
          },
          {
            id: 'grounds',
            label: 'Основания 52.x',
            count: TERMINATION_GROUNDS.length,
            render: () => (
              <Section title="Основания по инициативе работодателя" meta="Ст. 52 ТК РК · выборка">
                <ReferenceTable
                  rows={TERMINATION_GROUNDS}
                  columns={[
                    { key: 'code', label: 'Код' },
                    { key: 'event', label: 'Событие' },
                    { key: 'evidence', label: 'Что должно лежать в деле' }
                  ]}
                />
              </Section>
            )
          },
          {
            id: 'settlement',
            label: 'Расчёт',
            count: TERMINATION_SETTLEMENT.length,
            render: () => (
              <Section title="Расчёт и последний рабочий день" meta="Выплаты не позднее 3 рабочих дней">
                <ReferenceTable
                  rows={TERMINATION_SETTLEMENT}
                  columns={[
                    { key: 'component', label: 'Компонент' },
                    { key: 'rule', label: 'Правило' },
                    { key: 'owner', label: 'Источник / владелец' }
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
