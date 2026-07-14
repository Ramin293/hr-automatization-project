export interface DocumentReference {
  documentId: string;
  documentNumber: string;
}

export interface WorkflowReference {
  workflowInstanceId: string;
  workflowStep: string;
}

export interface DocumentGateway {
  createLeaveRequestDocument(input: { employeeId: string; startDate: string; endDate: string; idempotencyKey: string; correlationId: string }): Promise<DocumentReference>;
}

export interface WorkflowGateway {
  startLeaveRequest(input: { leaveRequestBusinessKey: string; employeeId: string; managerId?: string; correlationId: string }): Promise<WorkflowReference>;
}

export const DOCUMENT_GATEWAY = Symbol('DOCUMENT_GATEWAY');
export const WORKFLOW_GATEWAY = Symbol('WORKFLOW_GATEWAY');
