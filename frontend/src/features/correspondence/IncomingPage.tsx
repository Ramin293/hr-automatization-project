import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CalendarDays, Download, Filter, LayoutGrid, List, Plus, Search, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { repositories } from '../../repositories';
import { EmptyState, PageHeader, QueryState } from '../../shared/components';
import { formatDate, statusLabels } from '../../shared/format';
import { useDeveloperStore } from '../../shared/store';

export default function IncomingPage() {
  const locale = useDeveloperStore((state) => state.locale);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');
  const result = useQuery({ queryKey: ['incoming'], queryFn: () => repositories.correspondence.listIncoming() });
  const filtered = useMemo(() => (result.data ?? []).filter((item) => (status === 'all' || item.status === status) && `${item.number} ${item.sender} ${item.subject}`.toLowerCase().includes(query.toLowerCase())), [result.data, query, status]);
  return <>
    <PageHeader eyebrow="Секретариат · Реестр" title="Входящая корреспонденция" description="Регистрация, маршрутизация и контроль исполнения входящих документов." actions={<><button className="secondary-button"><Download size={16} /> Экспорт</button><Link className="primary-button" to="/correspondence/incoming/new"><Plus size={16} /> Зарегистрировать письмо</Link></>} />
    <div className="register-summary"><span><strong>{result.data?.length ?? 0}</strong> всего в очереди</span><span><strong>3</strong> требуют резолюции</span><span><strong className="text-coral">2</strong> срочных</span><span><strong>1</strong> без вложений</span></div>
    <div className="register-toolbar"><label className="field-search"><Search size={16} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Номер, отправитель или тема" /></label><select value={status} onChange={(e) => setStatus(e.target.value)}><option value="all">Все статусы</option><option value="resolution">На резолюции</option><option value="execution">В работе</option><option value="approval">На согласовании</option><option value="signature">На подписи</option><option value="dispatch">К отправке</option></select><button className="toolbar-button"><CalendarDays size={16} /> Период</button><button className="toolbar-button"><Filter size={16} /> Фильтры</button><button className="toolbar-button icon-only"><SlidersHorizontal size={16} /></button><span className="view-toggle"><button className="active"><List size={16} /></button><button><LayoutGrid size={16} /></button></span></div>
    {result.isLoading ? <QueryState /> : result.error ? <QueryState error={result.error} retry={() => result.refetch()} /> : filtered.length === 0 ? <EmptyState title="Ничего не найдено" text="Измените запрос или сбросьте фильтры реестра." /> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Рег. номер</th><th>Получено</th><th>Отправитель / тема</th><th>Подразделение</th><th>Статус</th><th>Срок</th><th>SLA</th></tr></thead><tbody>{filtered.map((item) => <tr key={item.id} onClick={() => location.assign(`/correspondence/incoming/${item.id}`)}><td><Link to={`/correspondence/incoming/${item.id}`}><strong>{item.number}</strong><small>{item.senderNumber}</small></Link></td><td>{formatDate(item.receivedAt, locale, 'dd MMM')}<small>{formatDate(item.receivedAt, locale, 'HH:mm')}</small></td><td className="subject-cell"><strong>{item.sender}</strong><span>{item.subject}</span></td><td>{item.department}<small>{item.executor}</small></td><td><span className={`status-pill status-${item.status}`}><i />{statusLabels[item.status]}</span><small>{item.workflowStep}</small></td><td className={item.priority === 'urgent' ? 'text-coral' : ''}>{formatDate(item.dueDate, locale, 'dd MMM yyyy')}</td><td><span className={`sla-chip ${item.priority === 'urgent' ? 'risk' : ''}`}>{item.priority === 'urgent' ? '1д 4ч' : '6д'}</span></td></tr>)}</tbody></table></div>}
  </>;
}
