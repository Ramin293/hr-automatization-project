# Add Employee Frontend

## Purpose and route

`/hr/hiring/add-employee` is the only item in Hiring. It prepares an official management memorandum for a future employee; it does not create an employee account or start an approval workflow. The shared application shell, HR permission model and existing panel/form/dialog styles are reused.

## Form

The seven sections cover the recipient, current HR initiator, personal data, proposed employment, education and qualifications, local attachments and editable request text. Executives, departments, teams, positions, managers, employment types, work arrangements, schedules, reasons, education levels and currencies come from `referenceData.ts`, never from a backend.

Selecting an executive fills the recipient position, department and type. The initiator defaults to the development HR user. Salary is rendered only for `hr.sensitive.read`. The formal request text is regenerated from employee name, position, department, start date and reason until the user edits it manually.

## Validation

Zod enforces required fields, a 12-digit IIN, email and phone formats, past date of birth, a reasonable start date, identity expiry after issue, non-negative salary/probation and FTE limits. Errors render next to fields. Attachments accept PDF, DOC, DOCX, JPG and PNG up to 10 MB. Invalid files are rejected locally; accepted files can be removed.

## Draft lifecycle

`ertis.hr.add-employee.draft.v1` stores `{ values, savedAt }` in localStorage. Files are deliberately excluded. A saved draft is restored after refresh and HR Home shows its count and timestamp. Clear Form requires confirmation and removes both form values and the draft. Unsaved changes register a browser leave warning.

## Preview and DOCX

Preview renders a formal memorandum without downloading. Generate validates the form, shows a loading/error/success state, creates an A4 DOCX in the browser with Arial, standard margins and consistent spacing, then downloads `Employee_Hiring_Request_[LastName]_[FirstName]_[Date].docx`.

The document includes aligned recipient/sender information, date, heading, request text, personal and employment details, education, justification, a numbered attachment summary, initiator signature and management resolution areas. Russian is the current document language; pure builders keep a future Kazakh template possible.

## Architecture and limitations

React Hook Form owns local form state. `schema.ts`, `referenceData.ts`, `defaults.ts`, `draft.ts`, `utils.ts` and `docx.ts` keep validation, mock references, persistence and generation out of the page. Unit tests cover schema rules, IIN, names, request text, filenames, attachments and draft lifecycle.

No API, upload, database, server draft, employee persistence, email, EDS or Camunda Hiring process is invoked. `AddEmployeeSubmissionRepository` is documentation for a future separately reviewed integration and has no implementation or call site.
