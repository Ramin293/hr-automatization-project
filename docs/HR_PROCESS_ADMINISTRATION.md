# HR Process Administration

HR uses the shared Workflow/Camunda boundary. Process definitions, routing and human tasks remain shared assets and may be configured/versioned there. Domain modules store only workflow references and validate callback correlation, expected state and idempotency.

Add Employee is excluded: it creates no task, workflow command, Camunda process, worker or event.
