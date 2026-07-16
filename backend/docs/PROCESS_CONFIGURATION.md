# Process configuration

The seed publishes recruitment, hiring and termination process version 1 using stable codes/UUIDs.
All actors, document requirements, forms and conditions remain editable through new drafts.

Recruitment starts with HR completeness, staffing/finance review and vacancy management; its step
configuration also carries screening criteria and commission rules. Hiring uses candidate document
collection, contract/order and parallel onboarding. Termination uses HR review, conditional legal
behavior in the case, signature/registration and parallel offboarding.

Seeded form versions are `candidate_application`, `hiring_checklist` and
`offboarding_checklist`. Fields contain type, required flag, declarative validation, reference
source, visibility/editability data, confidentiality, ordering and help text. A submission with a
process instance must use a version ID captured in that instance snapshot.

Seed is deterministic and idempotent: rerunning it adds no duplicate permissions, forms, document
types, routes or reference values. Display names never participate in authorization or routing.
