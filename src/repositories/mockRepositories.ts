import { seedCorrespondence, seedEmployees, seedProcesses, seedTasks } from '../mocks/database';
import type { Correspondence, IncomingLetterInput, ProcessDefinition, WorkTask } from '../shared/types';
import type { CorrespondenceRepository, OperationsRepository, OrganizationRepository, TaskRepository, WorkflowRepository } from './contracts';

const DB_KEY = 'ertis-operations-mock-v1';
type MockDatabase = { correspondence: Correspondence[]; tasks: WorkTask[]; processes: ProcessDefinition[] };

const copy = <T,>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const initialDatabase = (): MockDatabase => ({ correspondence: copy(seedCorrespondence), tasks: copy(seedTasks), processes: copy(seedProcesses) });

function readDatabase(): MockDatabase {
  const stored = localStorage.getItem(DB_KEY);
  if (!stored) return initialDatabase();
  try { return JSON.parse(stored) as MockDatabase; } catch { return initialDatabase(); }
}

function writeDatabase(database: MockDatabase) {
  localStorage.setItem(DB_KEY, JSON.stringify(database));
}

const wait = async <T,>(value: T): Promise<T> => new Promise((resolve) => window.setTimeout(() => resolve(copy(value)), 180));

export class MockCorrespondenceRepository implements CorrespondenceRepository {
  async listIncoming() { return wait(readDatabase().correspondence); }

  async getIncoming(id: string) {
    const item = readDatabase().correspondence.find((entry) => entry.id === id);
    if (!item) throw new Error('CORRESPONDENCE_NOT_FOUND');
    return wait(item);
  }

  async checkDuplicate(sender: string, senderNumber: string) {
    const item = readDatabase().correspondence.find((entry) => entry.sender === sender && entry.senderNumber.toLowerCase() === senderNumber.toLowerCase());
    return wait(item ?? null);
  }

  async registerIncoming(input: IncomingLetterInput) {
    const database = readDatabase();
    const sequence = 843 + database.correspondence.filter((item) => item.id.startsWith('inc-new')).length;
    const number = `ВХ-2026-${String(sequence).padStart(6, '0')}`;
    const item: Correspondence = {
      id: `inc-new-${sequence}`, number, sender: input.sender, senderNumber: input.senderNumber, senderDate: input.senderDate,
      receivedAt: new Date().toISOString(), subject: input.subject, summary: input.summary, documentType: input.documentType,
      channel: input.channel, department: input.department || 'Не определён', executive: input.executive || 'Не определён', executor: 'Не назначен',
      dueDate: input.dueDate, priority: input.priority, status: 'registered', workflowStep: 'Проверка секретариатом', confidentiality: input.confidentiality,
      responseRequired: input.responseRequired, attachments: [], tags: [], audit: [{ id: `audit-${sequence}`, at: new Date().toISOString(), actor: 'Алия Омарова', action: 'Зарегистрировано', detail: `Registry mock присвоил номер ${number}` }]
    };
    database.correspondence.unshift(item);
    writeDatabase(database);
    return wait(item);
  }

  async sendForResolution(id: string) {
    const database = readDatabase();
    const item = database.correspondence.find((entry) => entry.id === id);
    if (!item) throw new Error('CORRESPONDENCE_NOT_FOUND');
    item.status = 'resolution';
    item.workflowStep = 'Резолюция руководителя';
    item.audit.unshift({ id: `audit-${Date.now()}`, at: new Date().toISOString(), actor: 'Алия Омарова', action: 'Направлено на резолюцию', detail: item.executive });
    writeDatabase(database);
    return wait(item);
  }
}

export class MockTaskRepository implements TaskRepository {
  async list() { return wait(readDatabase().tasks); }
  async claim(id: string) { return this.update(id, 'claimed', 'Алия Омарова'); }
  async complete(id: string) { return this.update(id, 'completed'); }
  private async update(id: string, state: WorkTask['state'], assignee?: string) {
    const database = readDatabase();
    const task = database.tasks.find((entry) => entry.id === id);
    if (!task) throw new Error('TASK_NOT_FOUND');
    task.state = state;
    if (assignee) task.assignee = assignee;
    writeDatabase(database);
    return wait(task);
  }
}

export class MockWorkflowRepository implements WorkflowRepository {
  async listDefinitions() { return wait(readDatabase().processes); }
  async retryIncident(id: string) {
    const database = readDatabase();
    const process = database.processes.find((entry) => entry.id === id);
    if (!process) throw new Error('PROCESS_NOT_FOUND');
    process.state = 'published';
    writeDatabase(database);
    return wait(process);
  }
}

export class MockOrganizationRepository implements OrganizationRepository {
  async listEmployees() { return wait(seedEmployees); }
}

export class MockOperationsRepository implements OperationsRepository {
  async dashboard() {
    const database = readDatabase();
    return wait({
      incomingToday: database.correspondence.filter((item) => item.receivedAt.startsWith('2026-07-14')).length,
      awaitingResolution: database.correspondence.filter((item) => item.status === 'resolution').length,
      activeTasks: database.tasks.filter((item) => item.state !== 'completed').length,
      overdue: database.tasks.filter((item) => item.state === 'overdue').length,
      signatureQueue: database.correspondence.filter((item) => item.status === 'signature').length,
      dispatchQueue: database.correspondence.filter((item) => item.status === 'dispatch').length
    });
  }
  async reset() { localStorage.removeItem(DB_KEY); }
}
