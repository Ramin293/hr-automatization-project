# Process administration

Operations users monitor definitions, active instances, incidents, current nodes, timers and candidate groups. Incident retry is a command with audit context, not an automatic browser loop. The v1.0.1 mock permits safe retry without changing external systems.

Production process administration must go through the BFF and Workflow Orchestration Service. Camunda credentials never enter the frontend.
