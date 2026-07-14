import type { PropsWithChildren, ReactNode } from 'react';
import { AlertTriangle, ArrowUpRight, FileX2, RefreshCw } from 'lucide-react';

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description?: string; actions?: ReactNode }) {
  return <header className="page-header"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1>{description && <p>{description}</p>}</div>{actions && <div className="page-actions">{actions}</div>}</header>;
}

export function Section({ title, meta, children, className = '' }: PropsWithChildren<{ title: string; meta?: string; className?: string }>) {
  return <section className={`panel ${className}`}><header className="panel-header"><h2>{title}</h2>{meta && <span>{meta}</span>}</header>{children}</section>;
}

export function QueryState({ error, retry }: { error?: Error | null; retry?: () => void }) {
  if (!error) return <div className="page-loading"><span /><span /><span /></div>;
  return <div className="empty-state"><AlertTriangle size={28} /><h2>Не удалось загрузить данные</h2><p>{error.message}</p>{retry && <button className="secondary-button" onClick={retry}><RefreshCw size={16} /> Повторить</button>}</div>;
}

export function EmptyState({ title, text }: { title: string; text: string }) {
  return <div className="empty-state"><FileX2 size={28} /><h2>{title}</h2><p>{text}</p></div>;
}

export function LinkArrow() { return <ArrowUpRight size={15} />; }
