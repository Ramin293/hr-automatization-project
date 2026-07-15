import { createContext, useContext, useMemo, type PropsWithChildren } from 'react';
import { useLocation } from 'react-router-dom';
import { getPermissions } from '../../../shared/permissions';
import { useDeveloperStore } from '../../../shared/store';
import type { PersonaId } from '../../../shared/types';

type DepartmentContextValue = { departmentId: string | null; departmentCode: 'HR' | null; departmentName: string | null; pageTitle: string; role: PersonaId; permissions: string[] };
const DepartmentContext = createContext<DepartmentContextValue>({ departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Главная', role: 'secretary', permissions: [] });

const hrPages: Array<[RegExp, string]> = [
  [/\/employees\/[^/]+$/, 'Профиль сотрудника'], [/\/employees$/, 'Сотрудники'],
  [/\/hiring\/add-employee$/, 'Добавить сотрудника'], [/\/leave$/, 'Отпуска'],
  [/\/sick-leave$/, 'Больничные'], [/\/business-trips$/, 'Командировки'],
  [/\/absence-calendar$/, 'Календарь отсутствий'], [/\/onboarding$/, 'Адаптация'],
  [/\/probation$/, 'Испытательный срок'], [/\/terminations$/, 'Увольнения'],
  [/\/offboarding$/, 'Оффбординг'], [/\/messages$/, 'Входящие сообщения'],
  [/\/analytics$/, 'Аналитика'], [/\/(hr|departments\/hr)\/?$/, 'Главная']
];

export function DepartmentProvider({ children }: PropsWithChildren) {
  const { pathname } = useLocation();
  const persona = useDeveloperStore((state) => state.persona);
  const value = useMemo<DepartmentContextValue>(() => {
    const isHr = pathname === '/hr' || pathname.startsWith('/hr/') || pathname === '/departments/hr' || pathname.startsWith('/departments/hr/');
    const base = { role: persona, permissions: getPermissions(persona) as string[] };
    if (isHr) return { ...base, departmentId: 'department-hr', departmentCode: 'HR', departmentName: 'Департамент управления персоналом', pageTitle: hrPages.find(([pattern]) => pattern.test(pathname))?.[1] ?? 'Рабочее пространство' };
    if (pathname.includes('incoming')) return { ...base, departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Входящая корреспонденция' };
    if (pathname.includes('tasks')) return { ...base, departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Задачи' };
    if (pathname.includes('processes')) return { ...base, departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Процессы' };
    if (pathname.includes('organization')) return { ...base, departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Организация' };
    return { ...base, departmentId: null, departmentCode: null, departmentName: null, pageTitle: 'Главная' };
  }, [pathname, persona]);
  return <DepartmentContext.Provider value={value}>{children}</DepartmentContext.Provider>;
}

export const useDepartmentContext = () => useContext(DepartmentContext);
