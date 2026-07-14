# Document model

`Correspondence` is the case record. It references the original document, attachments, routing metadata, SLA, participants and audit events. A future `Document` aggregate owns content and immutable versions; `RegistryEntry` owns legal numbering; `WorkflowInstance` owns process state.

Original inbound files, secretariat metadata, executive resolution, contributions, response draft, signed response and dispatch evidence remain distinct objects even when shown on one case page.
