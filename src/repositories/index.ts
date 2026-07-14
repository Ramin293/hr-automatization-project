import { MockCorrespondenceRepository, MockOperationsRepository, MockOrganizationRepository, MockTaskRepository, MockWorkflowRepository } from './mockRepositories';

export const repositories = {
  correspondence: new MockCorrespondenceRepository(),
  tasks: new MockTaskRepository(),
  workflows: new MockWorkflowRepository(),
  organization: new MockOrganizationRepository(),
  operations: new MockOperationsRepository()
};
