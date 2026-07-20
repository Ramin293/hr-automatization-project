import { useState, type ReactNode } from 'react';
import { FileText, GitBranch, ListChecks, ShieldQuestion, Users, Workflow } from 'lucide-react';
import { PageHeader, Section } from '../../shared/components';
import { DocumentRegistry, GateList, MetricRow, RoleMatrix, RuleCallout, SegmentTabs, StageTimeline, StatusBoard } from './components';
import type { DecisionGate, RegistryDocument, RoleDuty, StatusState, WorkflowStage } from './data/types';

export interface ProcessSystemConfig {
  meta: { eyebrow: string; title: string; description: string; version: string; rule: string };
  stages: WorkflowStage[];
  roles: RoleDuty[];
  gates: DecisionGate[];
  statuses: StatusState[];
  documents: RegistryDocument[];
  /** Domain-specific tabs inserted after «Роли» (routes, grounds, rubric …). */
  extraTabs?: Array<{ id: string; label: string; count?: number; render: () => ReactNode }>;
}

export function ProcessSystemPage({ config }: { config: ProcessSystemConfig }) {
  const [tab, setTab] = useState('route');
  const extra = config.extraTabs ?? [];
  const tabs = [
    { id: 'route', label: 'Маршрут', count: config.stages.length },
    { id: 'roles', label: 'Роли', count: config.roles.length },
    ...extra.map((item) => ({ id: item.id, label: item.label, count: item.count })),
    { id: 'documents', label: 'Документы', count: config.documents.length },
    { id: 'statuses', label: 'Статусы', count: config.statuses.length },
    { id: 'gates', label: 'Шлюзы', count: config.gates.length }
  ];

  return (
    <>
      <PageHeader eyebrow={config.meta.eyebrow} title={config.meta.title} description={config.meta.description} />
      <MetricRow
        items={[
          { label: 'Стадий маршрута', value: config.stages.length, hint: config.meta.version, tone: 'violet' },
          { label: 'Ролей и полномочий', value: config.roles.length, hint: 'с разграничением запретов', tone: 'teal' },
          { label: 'Форм в реестре', value: config.documents.length, hint: 'типовые документы', tone: 'gold' },
          { label: 'Контрольных шлюзов', value: config.gates.length, hint: 'автоматические проверки', tone: 'coral' }
        ]}
      />
      <RuleCallout>{config.meta.rule}</RuleCallout>
      <SegmentTabs tabs={tabs} active={tab} onChange={setTab} />

      {tab === 'route' && (
        <Section title="Сквозной маршрут" meta={`${config.stages.length} стадий · фазы жизненного цикла`}>
          <div className="wf-legend"><Workflow size={15} /> Нажмите на стадию, чтобы выделить её. Владелец и SLA закреплены регламентом.</div>
          <StageTimeline stages={config.stages} />
        </Section>
      )}
      {tab === 'roles' && (
        <Section title="Роли, полномочия и запреты" meta={`${config.roles.length} ролей`}>
          <div className="wf-legend"><Users size={15} /> Каждая роль ограничена явным запретом — разделение обязанностей заложено в модель.</div>
          <RoleMatrix roles={config.roles} />
        </Section>
      )}
      {extra.map((item) => (tab === item.id ? <div key={item.id}>{item.render()}</div> : null))}
      {tab === 'documents' && (
        <Section title="Реестр документов" meta={`${config.documents.length} типовых форм`}>
          <div className="wf-legend"><FileText size={15} /> Пустой документ не подписывается; подписант определяется по Уставу или доверенности.</div>
          <DocumentRegistry documents={config.documents} />
        </Section>
      )}
      {tab === 'statuses' && (
        <Section title="Статусы и бизнес-логика" meta="Camunda / BPMN">
          <div className="wf-legend"><GitBranch size={15} /> Подписанные документы и решения не редактируются задним числом.</div>
          <StatusBoard statuses={config.statuses} />
        </Section>
      )}
      {tab === 'gates' && (
        <Section title="Решающие шлюзы" meta={`${config.gates.length} проверок`}>
          <div className="wf-legend"><ShieldQuestion size={15} /> Шлюзы блокируют переход, пока условие не выполнено.</div>
          <GateList gates={config.gates} />
        </Section>
      )}
      {tab === 'documents' && (
        <p className="wf-footnote"><ListChecks size={13} /> Полный реестр насчитывает больше форм; здесь приведены ключевые из регламента-проекта.</p>
      )}
    </>
  );
}
