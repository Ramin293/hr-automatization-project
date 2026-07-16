import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeftRight, UserX, X } from 'lucide-react';
import { useState, type FormEvent, type ReactNode } from 'react';
import { hrRepository } from '../api';
import type { EmployeeFunctionDescriptor } from '../model/types';

const functionIcons: Record<string, ReactNode> = {
  'employee.terminate': <UserX size={16} />,
  'employee.transfer': <ArrowLeftRight size={16} />
};

const today = () => new Date().toISOString().slice(0, 10);

function FunctionDialog({ descriptor, onClose, onSubmit, error, pending, children }: {
  descriptor: EmployeeFunctionDescriptor;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  error: string;
  pending: boolean;
  children: ReactNode;
}) {
  return <div className="dialog-backdrop">
    <section className="dialog hr-confirm-dialog" role="dialog" aria-modal="true" aria-label={descriptor.title}>
      <header><span>{descriptor.title}</span><button type="button" className="icon-button" onClick={onClose} aria-label="Закрыть"><X size={18} /></button></header>
      <form onSubmit={onSubmit}>
        <p>{descriptor.description}</p>
        <div className="field-grid">{children}</div>
        {error && <div className="hr-attachment-error" role="alert">{error}</div>}
        <footer>
          <button type="button" className="secondary-button" onClick={onClose}>Отмена</button>
          <button type="submit" className="primary-button" disabled={pending}>{pending ? 'Выполняется…' : descriptor.title}</button>
        </footer>
      </form>
    </section>
  </div>;
}

function useInvokeFunction(employeeId: string, onDone: () => void) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ key, payload }: { key: string; payload: Record<string, unknown> }) =>
      hrRepository.invokeEmployeeFunction(employeeId, key, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['hr'] }),
        queryClient.invalidateQueries({ queryKey: ['employee-functions'] })
      ]);
      onDone();
    }
  });
}

function TerminateDialog({ employeeId, descriptor, onClose }: { employeeId: string; descriptor: EmployeeFunctionDescriptor; onClose: () => void }) {
  const [terminationDate, setTerminationDate] = useState(today());
  const [reason, setReason] = useState('');
  const invoke = useInvokeFunction(employeeId, onClose);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const record = await hrRepository.getCoreEmployee(employeeId);
    invoke.mutate({ key: descriptor.key, payload: { terminationDate, reason, revision: record.revision } });
  };

  return <FunctionDialog descriptor={descriptor} onClose={onClose} onSubmit={submit} error={invoke.error ? String(invoke.error.message) : ''} pending={invoke.isPending}>
    <label>Дата увольнения<em>*</em><input type="date" value={terminationDate} onChange={(event) => setTerminationDate(event.target.value)} required /></label>
    <label className="span-two">Причина<em>*</em><textarea value={reason} onChange={(event) => setReason(event.target.value)} rows={3} placeholder="Основание увольнения" required /></label>
  </FunctionDialog>;
}

function TransferDialog({ employeeId, descriptor, onClose }: { employeeId: string; descriptor: EmployeeFunctionDescriptor; onClose: () => void }) {
  const [staffingSlotId, setStaffingSlotId] = useState('');
  const [effectiveFrom, setEffectiveFrom] = useState(today());
  const [reason, setReason] = useState('');
  const slots = useQuery({ queryKey: ['staffing-slots', 'vacant'], queryFn: () => hrRepository.listVacantSlots() });
  const invoke = useInvokeFunction(employeeId, onClose);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    invoke.mutate({ key: descriptor.key, payload: { staffingSlotId, effectiveFrom, reason } });
  };

  return <FunctionDialog descriptor={descriptor} onClose={onClose} onSubmit={submit} error={invoke.error ? String(invoke.error.message) : ''} pending={invoke.isPending}>
    <label className="span-two">Новая штатная единица<em>*</em>
      <select value={staffingSlotId} onChange={(event) => setStaffingSlotId(event.target.value)} required>
        <option value="">{slots.isLoading ? 'Загрузка…' : 'Выберите'}</option>
        {(slots.data ?? []).map((slot) => <option key={slot.id} value={slot.id}>{slot.label}</option>)}
      </select>
    </label>
    <label>Дата перевода<em>*</em><input type="date" value={effectiveFrom} onChange={(event) => setEffectiveFrom(event.target.value)} required /></label>
    <label className="span-two">Причина<em>*</em><textarea value={reason} onChange={(event) => setReason(event.target.value)} rows={3} placeholder="Основание перевода" required /></label>
  </FunctionDialog>;
}

export function EmployeeActions({ employeeId }: { employeeId: string }) {
  const functions = useQuery({
    queryKey: ['employee-functions', employeeId],
    queryFn: () => hrRepository.listEmployeeFunctions(employeeId)
  });
  const [active, setActive] = useState<EmployeeFunctionDescriptor | null>(null);
  const supported = new Set(['employee.terminate', 'employee.transfer']);
  if (!functions.data?.length) return null;

  return <>
    {functions.data.map((descriptor) => (
      <button
        key={descriptor.key}
        type="button"
        className="secondary-button"
        disabled={!supported.has(descriptor.key)}
        title={supported.has(descriptor.key) ? descriptor.description : 'Форма для этой функции ещё не подключена'}
        onClick={() => setActive(descriptor)}
      >
        {functionIcons[descriptor.key]}{descriptor.title}
      </button>
    ))}
    {active?.key === 'employee.terminate' && <TerminateDialog employeeId={employeeId} descriptor={active} onClose={() => setActive(null)} />}
    {active?.key === 'employee.transfer' && <TransferDialog employeeId={employeeId} descriptor={active} onClose={() => setActive(null)} />}
  </>;
}
