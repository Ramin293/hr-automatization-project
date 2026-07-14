# HR Service Boundaries

| Boundary | Owns | Does not own |
| --- | --- | --- |
| HR Core | employee, department projection, position projection, staffing position | identity accounts, files, tasks |
| HR Absence | leave balance, leave request, approval state | workflow engine, generated document binary |
| Common platform ports | typed calls to documents and workflow | HR business decisions |
| Outbox | durable integration intent | broker delivery implementation |

Department and position are local authoritative records for this greenfield backend. If an enterprise organization service is introduced, they become synchronized read models and ownership moves via an ADR and migration.

Potential future extraction is driven by independent scaling or ownership, not by entity count. Module code must communicate through application interfaces before extraction.
