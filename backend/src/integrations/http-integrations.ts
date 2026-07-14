import { errors } from '../common/domain-error';
import { DocumentGateway, DocumentReference, WorkflowGateway, WorkflowReference } from './integration.ports';

async function postJson<T>(baseUrl: string | undefined, path: string, input: object, correlationId: string, service: string): Promise<T> {
  if (!baseUrl) throw errors.integration(service);
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, '')}${path}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-correlation-id': correlationId },
      body: JSON.stringify(input),
      signal: AbortSignal.timeout(5_000)
    });
    if (!response.ok) throw new Error(`${service} returned ${response.status}`);
    return await response.json() as T;
  } catch (error: unknown) {
    process.stdout.write(`${JSON.stringify({ level: 'error', event: 'integration.request.failed', service, correlationId, error: error instanceof Error ? error.message : 'unknown error' })}\n`);
    throw errors.integration(service);
  }
}

export class HttpDocumentGateway implements DocumentGateway {
  async createLeaveRequestDocument(input: { employeeId: string; startDate: string; endDate: string; idempotencyKey: string; correlationId: string }) {
    const result = await postJson<DocumentReference>(process.env.DOCUMENT_SERVICE_URL, '/api/v1/documents/hr/leave-requests', input, input.correlationId, 'document-service');
    if (!result.documentId || !result.documentNumber) throw errors.integration('document-service');
    return result;
  }
}

export class HttpWorkflowGateway implements WorkflowGateway {
  async startLeaveRequest(input: { leaveRequestBusinessKey: string; employeeId: string; managerId?: string; correlationId: string }) {
    const result = await postJson<WorkflowReference>(process.env.WORKFLOW_SERVICE_URL, '/api/v1/workflows/leave-requests', input, input.correlationId, 'workflow-service');
    if (!result.workflowInstanceId || !result.workflowStep) throw errors.integration('workflow-service');
    return result;
  }
}
