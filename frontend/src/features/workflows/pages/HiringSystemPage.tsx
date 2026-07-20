import { Section } from '../../../shared/components';
import { ReferenceTable } from '../components';
import { ProcessSystemPage } from '../ProcessSystemPage';
import { HIRING_DOCUMENTS, HIRING_GATES, HIRING_META, HIRING_ROLES, HIRING_RUBRIC, HIRING_SCENARIOS, HIRING_STAGES, HIRING_STATUSES } from '../data/hiring';

export default function HiringSystemPage() {
  return (
    <ProcessSystemPage
      config={{
        meta: HIRING_META,
        stages: HIRING_STAGES,
        roles: HIRING_ROLES,
        gates: HIRING_GATES,
        statuses: HIRING_STATUSES,
        documents: HIRING_DOCUMENTS,
        extraTabs: [
          {
            id: 'rubric',
            label: 'Рубрика оценки',
            count: HIRING_RUBRIC.length,
            render: () => (
              <Section title="Система оценки конкурсной комиссии" meta={HIRING_META.quorum}>
                <ReferenceTable
                  rows={HIRING_RUBRIC}
                  columns={[
                    { key: 'criterion', label: 'Критерий' },
                    { key: 'weight', label: 'Вес' },
                    { key: 'assesses', label: 'Что оценивается' },
                    { key: 'assessor', label: 'Кто' }
                  ]}
                />
              </Section>
            )
          },
          {
            id: 'scenarios',
            label: 'Сценарии',
            count: HIRING_SCENARIOS.length,
            render: () => (
              <Section title="Специальные сценарии найма" meta={`${HIRING_SCENARIOS.length} маршрутов`}>
                <ReferenceTable
                  rows={HIRING_SCENARIOS}
                  columns={[
                    { key: 'scenario', label: 'Сценарий' },
                    { key: 'route', label: 'Маршрут' },
                    { key: 'rule', label: 'Жёсткое правило' }
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
