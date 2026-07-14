import { Injectable } from '@nestjs/common';
import { createHash } from 'crypto';
import { DocumentGateway, DocumentReference, WorkflowGateway, WorkflowReference } from './integration.ports';

const stableSuffix = (value: string) => createHash('sha256').update(value).digest('hex').slice(0, 10);

@Injectable()
export class MockDocumentGateway implements DocumentGateway {
  async createLeaveRequestDocument(input: { idempotencyKey: string }): Promise<DocumentReference> {
    const suffix = stableSuffix(input.idempotencyKey).toUpperCase();
    return { documentId: `mock-document-${suffix}`, documentNumber: `HR-LV-${new Date().getUTCFullYear()}-${suffix.slice(0, 6)}` };
  }
}

@Injectable()
export class MockWorkflowGateway implements WorkflowGateway {
  async startLeaveRequest(input: { leaveRequestBusinessKey: string }): Promise<WorkflowReference> {
    return { workflowInstanceId: `mock-workflow-${stableSuffix(input.leaveRequestBusinessKey)}`, workflowStep: 'MANAGER_REVIEW' };
  }
}
