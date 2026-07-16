# Future integrations

The current module makes external work visible and auditable but never claims a fake success.

| Boundary | Current behavior | Future adapter |
| --- | --- | --- |
| Electronic signature | provider status model; manual confirmation only in development | qualified signature provider callbacks with idempotency |
| Job boards / Enbek | manual publication channel and external reference | publication/status synchronization |
| IAM | required access-revocation task | account disablement and evidence callback |
| Payroll | required settlement task | payroll final-calculation confirmation |
| Assets | required asset-return task | inventory/asset system confirmation |
| Notifications | workflow state and outbox records | email/SMS/push dispatcher |
| Document rendering | UTF-8 scalar placeholder adapter | DOCX/PDF rendering service |
| Workflow engine | local relational runtime | optional Camunda adapter only if product requirements justify it |

Safe outbox events already provide transactionally consistent integration inputs. Payloads contain
IDs/status only and must remain free of CVs, contacts, identity, compensation and restricted notes.
