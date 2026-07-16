import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { ArrowRight, CalendarCheck2, FileWarning, GraduationCap, UserCheck, UserPlus, UsersRound } from 'lucide-react';
import { Link } from 'react-router-dom';
import { repositories } from '../../../repositories';
import { PageHeader, QueryState, Section } from '../../../shared/components';
import { ActivityChart, BarChart, DonutChart } from '../../../shared/charts';
import { formatDate, statusLabels } from '../../../shared/format';
import { usePermission } from '../../../shared/permissions';
import { useDeveloperStore } from '../../../shared/store';
import { hrRepository } from '../api';
import { LeaveStatus } from '../components/HrStatus';

export default function HrOverviewPage() {
  const persona = useDeveloperStore((state) => state.persona);
  const locale = useDeveloperStore((state) => state.locale);
  const canOpen = usePermission('hr.read');
  const isHr = persona === 'hr-specialist';
  const [activityDays, setActivityDays] = useState<7 | 14>(7);
  const overview = useQuery({ queryKey: ['hr', 'overview'], queryFn: () => hrRepository.getOverview(), enabled: canOpen && isHr });
  const employee = useQuery({ queryKey: ['hr', 'employee', 'me'], queryFn: () => hrRepository.getCurrentEmployee(), enabled: canOpen && !isHr });
  const leaveRequests = useQuery({ queryKey: ['hr', 'leave'], queryFn: () => hrRepository.listLeaveRequests(), enabled: canOpen });
  const messages = useQuery({ queryKey: ['incoming'], queryFn: () => repositories.correspondence.listIncoming(), enabled: canOpen && isHr });
  const tasks = useQuery({ queryKey: ['tasks'], queryFn: () => repositories.tasks.list(), enabled: canOpen && isHr });

  if (!canOpen) return <div className="hr-access-denied"><span>HR</span><h1>Рабочее пространство недоступно</h1><p>Выбранная роль не участвует в HR self-service или кадровых процессах.</p><Link className="secondary-button" to="/">На главную</Link></div>;
  if (overview.isLoading || employee.isLoading || leaveRequests.isLoading || messages.isLoading || tasks.isLoading) return <QueryState />;
  const error = overview.error || employee.error || leaveRequests.error || messages.error || tasks.error;
  if (error) return <QueryState error={error} retry={() => { overview.refetch(); employee.refetch(); leaveRequests.refetch(); messages.refetch(); tasks.refetch(); }} />;

  if (!isHr) {
    const person = employee.data!;
    const ownRequests = leaveRequests.data!.filter((item) => item.employeeId === person.id);
    return <>
      <PageHeader eyebrow="HR · Сотрудник" title={`Здравствуйте, ${person.fullName.split(' ')[0]}`} actions={<Link className="primary-button" to="/hr/leave"><CalendarCheck2 size={16} /> Новая заявка</Link>} />
      <div className="hr-employee-hero">
        <div className="hr-person"><span className="avatar hr-avatar-xl">{person.initials}</span><div><strong>{person.fullName}</strong><span>{person.position} · {person.department}</span><small>{person.employeeNumber}</small></div></div>
        <div className="hr-balance"><span>Доступный отпуск</span><strong>{person.leaveBalance}<small>дней</small></strong><i><b style={{ width: `${Math.min(100, person.leaveBalance / 28 * 100)}%` }} /></i></div>
        <div className="hr-file-score"><span>Личное дело</span><strong>{person.personnelFileCompleteness}%</strong><small>{person.personnelFileCompleteness < 100 ? 'Нужно дополнить документы' : 'Все документы на месте'}</small></div>
      </div>
      <div className="hr-dashboard-grid employee-view">
        <Section title="Мои заявки" meta={`${ownRequests.length} активных`}><div className="hr-request-list">{ownRequests.map((request) => <article key={request.id}><span className="hr-list-icon"><CalendarCheck2 size={17} /></span><div><strong>{request.leaveType}</strong><small>{formatDate(request.startDate, locale, 'dd MMM')} — {formatDate(request.endDate, locale, 'dd MMM yyyy')} · {request.days} дней</small></div><LeaveStatus status={request.status} /></article>)}</div><Link className="panel-link" to="/hr/leave">Открыть заявки <ArrowRight size={15} /></Link></Section>
        <Section title="Ближайшие события"><div className="hr-event-list"><div><span className="tone-violet"><GraduationCap size={17} /></span><div><strong>Оценка KPI за II квартал</strong><small>Заполнить самооценку до 20 июля</small></div></div><div><span className="tone-teal"><UserCheck size={17} /></span><div><strong>One-to-one с руководителем</strong><small>22 июля · 15:00</small></div></div><div><span className="tone-gold"><FileWarning size={17} /></span><div><strong>Обновить контактные данные</strong><small>Профиль заполнен на 92%</small></div></div></div></Section>
      </div>
    </>;
  }

  const stats = overview.data!;
  const pending = leaveRequests.data!.filter((item) => item.status === 'hr_review');
  const activeTasks = tasks.data!.filter((task) => task.state !== 'completed');
  const workforceTotal = Math.max(1, stats.activeEmployees + stats.onLeave + stats.onBusinessTrip + stats.onSickLeave);
  const presenceRate = Math.round(stats.activeEmployees / workforceTotal * 100);
  const workforceChart = [
    { label: 'Активны', value: stats.activeEmployees, color: 'var(--teal)', detail: 'На рабочем месте', to: '/hr/employees' },
    { label: 'В отпуске', value: stats.onLeave, color: 'var(--gold)', detail: 'Плановое отсутствие', to: '/hr/leave' },
    { label: 'Командировка', value: stats.onBusinessTrip, color: 'var(--violet)', detail: 'Служебная поездка', to: '/hr/calendar' },
    { label: 'Больничный', value: stats.onSickLeave, color: 'var(--coral)', detail: 'Нетрудоспособность', to: '/hr/sick-leave' },
  ];
  const controlChart = [
    { label: 'Процессы', value: stats.activeProcesses, color: 'var(--teal)', to: '/processes' },
    { label: 'Дела < 90%', value: stats.incompleteFiles, color: 'var(--gold)', to: '/hr/documents' },
    { label: 'Договоры', value: stats.expiringContracts, color: 'var(--violet)', to: '/hr/employees?query=2026' },
    { label: 'Просрочено', value: stats.overdueTasks, color: 'var(--coral)', to: '/tasks?filter=overdue' },
  ];
  const activityChart = Array.from({ length: activityDays }, (_, index) => {
    const day = new Date();
    day.setHours(0, 0, 0, 0);
    day.setDate(day.getDate() + index);
    const key = day.toISOString().slice(0, 10);
    const messageCount = messages.data!.filter((item) => item.dueDate.slice(0, 10) === key).length;
    const taskCount = activeTasks.filter((item) => item.dueDate.slice(0, 10) === key).length;
    const leaveCount = leaveRequests.data!.filter((item) => item.startDate.slice(0, 10) === key).length;
    return { label: day.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' }), value: messageCount + taskCount + leaveCount, detail: `${messageCount} сообщ. · ${taskCount} задач · ${leaveCount} отсутствий` };
  });

  return <>
    <PageHeader eyebrow="HR · Главная" title="Рабочее пространство" actions={<><Link className="secondary-button" to="/hr/employees"><UsersRound size={16} /> Сотрудники</Link><Link className="primary-button" to="/hr/employees?add=true"><UserPlus size={16} /> Добавить сотрудника</Link></>} />
    
    <div className="dashboard-chart-grid hr-dashboard-charts">
      <Section title="Структура присутствия" meta={`${workforceTotal} сотрудников`}><DonutChart data={workforceChart} centerValue={`${presenceRate}%`} centerLabel="активны" ariaLabel="Распределение сотрудников по типу присутствия" /></Section>
      <Section title="HR-контроль" meta="Актуальные риски"><BarChart data={controlChart} ariaLabel="HR-показатели, требующие контроля" /></Section>
    </div>

    <Section title="Активность" meta={`${activityDays} дней`} className="dashboard-activity-panel">
      <div className="dashboard-chart-toolbar"><span>Сроки сообщений, задач и начало отсутствий</span><div><button type="button" className={activityDays === 7 ? 'active' : ''} onClick={() => setActivityDays(7)}>7 дней</button><button type="button" className={activityDays === 14 ? 'active' : ''} onClick={() => setActivityDays(14)}>14 дней</button></div></div>
      <ActivityChart data={activityChart} ariaLabel={`Активность HR на ${activityDays} дней`} />
    </Section>

    <div className="hr-overview-row-split">
      <Section title="Входящие сообщения" meta={`${messages.data!.length} в очереди`}><div className="queue-table"><div className="table-head"><span>Сообщение</span><span>Отправитель</span><span>Этап</span><span>Срок</span><span /></div>{messages.data!.slice(0, 5).map((item) => <Link to={`/correspondence/incoming/${item.id}`} className="table-row" key={item.id}><span><strong>{item.number}</strong><small>{item.subject}</small></span><span>{item.sender}</span><span><i className={`status-dot status-${item.status}`} />{statusLabels[item.status]}</span><span className={item.priority === 'urgent' ? 'text-coral' : ''}>{formatDate(item.dueDate, locale, 'dd MMM')}</span><ArrowRight size={15} /></Link>)}</div><Link className="panel-link" to="/correspondence/incoming">Все сообщения <ArrowRight size={15} /></Link></Section>
      <Section title="Активные согласования" meta={`${pending.length} ожидают HR`}><div className="hr-request-list">{pending.length ? pending.map((request) => <Link to="/processes?id=p-hr-leave" key={request.id}><article><span className="hr-list-icon"><CalendarCheck2 size={17} /></span><div><strong>{request.employeeName}</strong><small>{request.leaveType} · {request.days} дней · {request.documentNumber}</small></div><LeaveStatus status={request.status} /></article></Link>) : <div className="hr-inline-empty">Очередь согласований пуста</div>}</div><Link className="panel-link" to="/processes">Открыть процессы <ArrowRight size={15} /></Link></Section>
    </div>

    <div className="hr-overview-row-single">
      <Section title="Задачи" meta={`${activeTasks.length} активных`}><div className="task-compact-list">{activeTasks.slice(0, 4).map((task) => <Link to="/tasks" key={task.id}><span className={`priority-line priority-${task.priority}`} /><span><strong>{task.title}</strong><small>{task.process} · до {formatDate(task.dueDate, locale, 'dd MMM')}</small></span><ArrowRight size={15} /></Link>)}</div><Link className="panel-link" to="/tasks">Все задачи <ArrowRight size={15} /></Link></Section>
    </div>
  </>;
}
