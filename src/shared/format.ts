import { format, parseISO } from 'date-fns';
import { enUS, kk, ru } from 'date-fns/locale';
import type { Locale } from './types';

const locales = { ru, kk, en: enUS };
export const formatDate = (value: string, locale: Locale, pattern = 'dd MMM yyyy') => format(parseISO(value), pattern, { locale: locales[locale] });
export const statusLabels = {
  draft: 'Черновик', registered: 'Зарегистрировано', resolution: 'На резолюции', execution: 'В работе', approval: 'На согласовании', signature: 'На подписи', dispatch: 'К отправке', completed: 'Завершено'
} as const;
