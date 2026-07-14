import { Module } from '@nestjs/common';
import { DOCUMENT_GATEWAY, WORKFLOW_GATEWAY } from '../integrations/integration.ports';
import { MockDocumentGateway, MockWorkflowGateway } from '../integrations/mock-integrations';
import { HttpDocumentGateway, HttpWorkflowGateway } from '../integrations/http-integrations';
import { EmployeeController } from './employee.controller';
import { EmployeeService } from './employee.service';
import { HR_REPOSITORY } from './hr.repository';
import { LeaveController } from './leave.controller';
import { LeaveService } from './leave.service';
import { PrismaHrRepository } from './prisma-hr.repository';

@Module({
  controllers: [EmployeeController, LeaveController],
  providers: [
    EmployeeService,
    LeaveService,
    PrismaHrRepository,
    { provide: HR_REPOSITORY, useExisting: PrismaHrRepository },
    { provide: DOCUMENT_GATEWAY, useFactory: () => process.env.NODE_ENV === 'production' || process.env.DOCUMENT_ADAPTER === 'http' ? new HttpDocumentGateway() : new MockDocumentGateway() },
    { provide: WORKFLOW_GATEWAY, useFactory: () => process.env.NODE_ENV === 'production' || process.env.WORKFLOW_ADAPTER === 'http' ? new HttpWorkflowGateway() : new MockWorkflowGateway() }
  ]
})
export class HrModule {}
