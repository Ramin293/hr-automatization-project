import { beforeEach, describe, expect, it } from 'vitest';
import { MockCorrespondenceRepository, MockTaskRepository, MockWorkflowRepository } from './mockRepositories';

describe('mock repository vertical flow', () => {
  beforeEach(() => localStorage.clear());

  it('assigns an official incoming number outside the page layer', async () => {
    const repository = new MockCorrespondenceRepository();
    const item = await repository.registerIncoming({ sender: 'Тестовая организация', senderType: 'organization', senderNumber: 'TEST-001', senderDate: '2026-07-14', channel: 'Email', documentType: 'Официальное письмо', subject: 'Проверка регистрационного номера', summary: 'Детерминированная проверка mock numbering service.', language: 'ru', pageCount: 1, confidentiality: 'internal', priority: 'normal', responseRequired: true, dueDate: '2026-07-21', department: 'Секретариат', executive: 'А. С. Нурланов', notes: '' });
    expect(item.number).toBe('ВХ-2026-000843');
    expect((await repository.listIncoming())[0].id).toBe(item.id);
  });

  it('claims and completes a task', async () => {
    const repository = new MockTaskRepository();
    expect((await repository.claim('t-102')).state).toBe('claimed');
    expect((await repository.complete('t-102')).state).toBe('completed');
  });

  it('retries a workflow incident safely in mock mode', async () => {
    const repository = new MockWorkflowRepository();
    expect((await repository.retryIncident('p-dispatch')).state).toBe('published');
  });
});
