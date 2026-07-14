# Microservice integration map

| Frontend feature | Repository | Future owner | Interaction |
| --- | --- | --- | --- |
| Incoming register and case | CorrespondenceRepository | Correspondence Service | Synchronous CRUD; events update search and audit |
| Official numbers | CorrespondenceRepository facade / RegistryRepository | Registry Service | Synchronous reservation and assignment |
| Task inbox | TaskRepository | Unified Task Inbox Service | Query and commands; workflow events update tasks |
| Process center | WorkflowRepository | Workflow Orchestration Service | Definitions, instances and incident commands |
| Employee directory | OrganizationRepository | Organization Service | Read models plus delegation events |
| Signature step | SignatureRepository | Signature Service | Signing command and asynchronous verification |
| Timeline | AuditRepository | Audit Service | Append-only read model |

The browser calls one API Gateway/BFF. Event-driven behavior remains behind that boundary; frontend polling or push notifications consume read models and never coordinate transactions.
