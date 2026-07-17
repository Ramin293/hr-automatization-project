import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, BriefcaseBusiness, CalendarDays, CheckCircle2, Clock, FileText, GraduationCap, Mail, MapPin, Phone, ShieldCheck, UserRound } from 'lucide-react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { PageHeader, QueryState } from '../../../shared/components';
import { formatDate } from '../../../shared/format';
import { usePermission } from '../../../shared/permissions';
import { useDeveloperStore } from '../../../shared/store';
import { hrRepository } from '../api';
import { EmployeeActions } from '../components/EmployeeActions';
import { EmployeeAbsencesSection } from '../components/EmployeeAbsencesSection';
import { TerminationSection } from '../components/TerminationSection';
import { EmployeeStatus } from '../components/HrStatus';

export default function HrEmployeeProfilePage() {
  const { employeeId = '' } = useParams();
  const [searchParams] = useSearchParams();
  const locale = useDeveloperStore((state) => state.locale);
  const canReadAll = usePermission('hr.employees.read');
  const canReadSensitive = usePermission('hr.sensitive.read');
  const currentEmployee = useQuery({
    queryKey: ['hr', 'employee', 'me'],
    queryFn: () => hrRepository.getCurrentEmployee(),
    enabled: !canReadAll
  });
  const isOwnProfile = currentEmployee.data?.id === employeeId;
  const allowed = canReadAll || isOwnProfile;
  const result = useQuery({ queryKey: ['hr', 'employee', employeeId], queryFn: () => hrRepository.getEmployee(employeeId), enabled: allowed });
  
  const [avatar, setAvatar] = useState<string | null>(() => localStorage.getItem(`employee-avatar-${employeeId}`));

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        setAvatar(base64);
        localStorage.setItem(`employee-avatar-${employeeId}`, base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerAvatarUpload = () => {
    document.getElementById('avatar-upload-input')?.click();
  };

  if (!canReadAll && currentEmployee.isLoading) return <QueryState />;
  if (!allowed) return <div className="hr-access-denied"><span>HR</span><h1>Профиль недоступен</h1><p>Сотрудник может просматривать только собственный профиль.</p><Link className="secondary-button" to="/departments/hr">Вернуться в HR</Link></div>;
  if (result.isLoading) return <QueryState />;
  if (result.error || !result.data) return <QueryState error={result.error ?? new Error('Сотрудник не найден')} retry={() => result.refetch()} />;
  const employee = result.data;
  const probationLabel = !employee.probationEnd
    ? 'Не предусмотрен'
    : employee.probationEnd >= new Date().toISOString().slice(0, 10)
      ? `до ${formatDate(employee.probationEnd, locale)}`
      : `Завершён ${formatDate(employee.probationEnd, locale)}`;

  return <>
    <PageHeader eyebrow={`Сотрудники · ${employee.employeeNumber}`} title={employee.fullName} description={`${employee.position} · ${employee.department}`} actions={<><EmployeeActions employeeId={employee.id} /><Link className="secondary-button" to={canReadAll ? '/departments/hr/employees' : '/departments/hr'}><ArrowLeft size={16} /> Назад</Link></>} />
    {searchParams.get('hired') === '1' && <div className="success-banner"><CheckCircle2 size={20} /><span><strong>Сотрудник зачислен в штат</strong>Карточка создана в backend и уже доступна в общем списке сотрудников.</span></div>}
    
    <div className="hiring-detail-grid">
      <section className="hiring-detail-main hiring-request-information">
        
        {/* Profile identity and customizable avatar */}
        <header className="hiring-panel-header" style={{ marginBottom: '20px' }}>
          <input 
            type="file" 
            accept="image/*" 
            id="avatar-upload-input" 
            style={{ display: 'none' }} 
            onChange={handleAvatarChange} 
          />
          <div 
            className="avatar hr-avatar-xl clickable-avatar" 
            style={{ 
              backgroundImage: avatar ? `url(${avatar})` : undefined, 
              backgroundSize: 'cover', 
              backgroundPosition: 'center', 
              cursor: 'pointer',
              width: '64px',
              height: '64px',
              borderRadius: '0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              fontWeight: 'bold',
              background: avatar ? undefined : 'var(--border)',
              color: 'var(--ink)'
            }}
            onClick={triggerAvatarUpload}
            title="Нажмите для смены аватара"
          >
            {!avatar && employee.initials}
          </div>
          <div style={{ marginLeft: '16px' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px' }}>
              <EmployeeStatus status={employee.status} />
              <span style={{ color: 'var(--muted)', fontSize: '12px' }}>{employee.employeeNumber}</span>
            </div>
            <strong style={{ fontSize: '18px', color: 'var(--ink)', display: 'block' }}>{employee.fullName}</strong>
            <span style={{ color: 'var(--muted)', fontSize: '13px' }}>{employee.position} · {employee.department}</span>
          </div>
          
          <div className="hr-profile-score" style={{ marginLeft: 'auto', borderLeft: '1px solid var(--border)', paddingLeft: '20px', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ color: 'var(--muted)', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Личное дело</span>
            <strong style={{ fontSize: '28px', color: 'var(--ink)', fontWeight: '800', marginTop: '4px' }}>{employee.personnelFileCompleteness}%</strong>
          </div>
        </header>

        {/* Contact info grid using hiring-information-grid */}
        <div className="hiring-information-grid" style={{ marginBottom: '24px' }}>
          <dl>
            <dt>Электронная почта</dt>
            <dd>{employee.workEmail}</dd>
          </dl>
          <dl>
            <dt>Телефон</dt>
            <dd>{employee.phone}</dd>
          </dl>
          <dl>
            <dt>Локация</dt>
            <dd>{employee.location}</dd>
          </dl>
        </div>

        {/* Рабочая информация */}
        <div className="hiring-information-section">
          <header className="hiring-panel-header">
            <span><BriefcaseBusiness size={20} /></span>
            <div>
              <strong>Рабочая информация</strong>
            </div>
          </header>
          <div className="hiring-information-grid cols-4">
            <dl>
              <dt>Табельный номер</dt>
              <dd>{employee.employeeNumber}</dd>
            </dl>
            <dl>
              <dt>Дата выхода</dt>
              <dd>{formatDate(employee.startDate, locale)}</dd>
            </dl>
            <dl>
              <dt>Тип занятости</dt>
              <dd>{employee.employmentType}</dd>
            </dl>
            <dl>
              <dt>Локация</dt>
              <dd>{employee.location}</dd>
            </dl>
            <dl>
              <dt>Руководитель</dt>
              <dd>{employee.manager ?? 'Не назначен'}</dd>
            </dl>
            <dl>
              <dt>Окончание договора</dt>
              <dd>{employee.contractEnd ? formatDate(employee.contractEnd, locale) : 'Бессрочный'}</dd>
            </dl>
            <dl>
              <dt>Испытательный срок</dt>
              <dd>{probationLabel}</dd>
            </dl>
          </div>
        </div>

        {/* Отсутствия */}
        <EmployeeAbsencesSection employeeId={employee.id} />

        {/* Увольнение */}
        <TerminationSection employee={employee} />

        {/* Компетенции и развитие */}
        <div className="hiring-information-section">
          <header className="hiring-panel-header">
            <span><GraduationCap size={20} /></span>
            <div>
              <strong>Компетенции и развитие</strong>
            </div>
          </header>
          
          <div className="hr-skill-list" style={{ padding: '0', display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
            {employee.skills.map((skill) => (
              <span key={skill} style={{ background: 'color-mix(in srgb, var(--violet) 8%, transparent)', border: '1px solid color-mix(in srgb, var(--violet) 25%, transparent)', borderRadius: '3px', color: 'var(--violet)', fontSize: '11px', padding: '6px 10px', fontWeight: '500' }}>
                {skill}
              </span>
            ))}
          </div>
          
          <div className="hr-development-note" style={{ border: '1px solid var(--border)', borderRadius: '0', background: 'var(--soft)', padding: '14px', display: 'flex', gap: '12px', alignItems: 'center' }}>
            <BriefcaseBusiness size={18} style={{ color: 'var(--teal)' }} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <strong style={{ fontSize: '13px', color: 'var(--ink)' }}>План развития на 2026 год</strong>
              <small style={{ color: 'var(--muted)', fontSize: '11px', marginTop: '2px' }}>2 цели в работе · следующая встреча 22 июля</small>
            </div>
          </div>
        </div>

        {/* Последняя активность */}
        <div className="hiring-information-section">
          <header className="hiring-panel-header">
            <span><Clock size={20} /></span>
            <div>
              <strong>Последняя активность</strong>
            </div>
          </header>
          <div className="audit-list" style={{ marginTop: '12px' }}>
            <div>
              <i />
              <span>
                <strong>Профиль сотрудника обновлён</strong>
                <small>HR Service · 12 июля</small>
                <p>Проверены контактные данные и место работы.</p>
              </span>
            </div>
            <div>
              <i />
              <span>
                <strong>Создана заявка на отпуск</strong>
                <small>Leave Request v2 · 14 июля</small>
                <p>Документ ожидает согласования руководителя.</p>
              </span>
            </div>
          </div>
        </div>

      </section>

      {/* Right Column: Aside */}
      <aside className="hiring-document-panel">
        
        {/* Отпуск */}
        <header className="hiring-panel-header">
          <span><CalendarDays size={20} /></span>
          <div>
            <strong>Отпуск</strong>
          </div>
        </header>
        <div className="hr-leave-card" style={{ border: '1px solid var(--border)', background: 'var(--soft)', padding: '16px', borderRadius: '0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <strong style={{ display: 'flex', flexDirection: 'column', fontSize: '24px', color: 'var(--ink)' }}>
            {employee.leaveBalance}
            <small style={{ color: 'var(--muted)', fontSize: '11px', fontWeight: 'normal', marginTop: '2px' }}>дней доступно</small>
          </strong>
          <Link to="/departments/hr/leave" className="secondary-button" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minHeight: '34px', padding: '0 12px', fontSize: '12px' }}>Создать заявку</Link>
        </div>

        {/* Компенсация */}
        <header className="hiring-panel-header">
          <span><ShieldCheck size={20} /></span>
          <div>
            <strong>Компенсация</strong>
          </div>
        </header>
        <div className="hr-sensitive-field" style={{ border: '1px solid var(--border)', background: 'var(--soft)', padding: '16px', borderRadius: '0', display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '24px' }}>
          <span style={{ color: 'var(--muted)', fontSize: '11px' }}>Текущий оклад</span>
          {canReadSensitive ? (
            <strong style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--ink)' }}>
              {new Intl.NumberFormat('ru-RU').format(employee.salary)} {employee.currency}
            </strong>
          ) : (
            <strong className="restricted-value"><ShieldCheck size={15} /> Ограничено</strong>
          )}
          <small style={{ color: 'var(--muted)', fontSize: '10px' }}>{canReadSensitive ? 'Ежемесячно · gross' : 'Требуется hr.sensitive.read'}</small>
        </div>

        {/* Документы */}
        <header className="hiring-panel-header">
          <span><FileText size={20} /></span>
          <div>
            <strong>Документы</strong>
          </div>
        </header>
        <div className="hiring-files" style={{ marginTop: '0' }}>
          <div className="hr-document-shortcuts" style={{ padding: '0', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '14px 16px', borderBottom: '1px solid var(--border)', background: 'var(--soft)', fontSize: '13px' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}><FileText size={16} /> Трудовой договор</span>
              <span className="hub-row-tag tag-success" style={{ background: 'color-mix(in srgb, var(--emerald) 12%, var(--paper))', color: '#067647', padding: '2px 6px', fontSize: '10px', fontWeight: 'bold' }}>активен</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '14px 16px', borderBottom: '1px solid var(--border)', background: 'var(--soft)', fontSize: '13px' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}><FileText size={16} /> Приказ о приёме</span>
              <span className="hub-row-tag tag-success" style={{ background: 'color-mix(in srgb, var(--emerald) 12%, var(--paper))', color: '#067647', padding: '2px 6px', fontSize: '10px', fontWeight: 'bold' }}>подписан</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '14px 16px', background: 'var(--soft)', fontSize: '13px' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}><UserRound size={16} /> Личная карточка</span>
              <span style={{ color: 'var(--muted)', fontSize: '12px' }}>{employee.personnelFileCompleteness}%</span>
            </div>
          </div>
        </div>

      </aside>
    </div>
  </>;
}
