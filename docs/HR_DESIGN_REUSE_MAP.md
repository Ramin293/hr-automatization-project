# HR Design Reuse Map

| HR surface | Existing reference | Reused implementation | Local extension |
|---|---|---|---|
| HR Home | Dashboard page and `Section` | AppShell, PageHeader, metric cards, panel grid | Add Employee shortcut card |
| Employees | Existing HR employees page | data table, toolbar, statuses, page header | HR terminology and filters |
| Employee profile | Existing HR profile | metadata grid, sensitive field state, panels | ATS groups removed |
| Leave | Existing HR leave page | form grid, route preview, panel layout | none |
| Add Employee | Existing leave/correspondence forms | PageHeader, Section, field-grid, buttons, dialogs, notifications | local reference data, attachment list and memorandum preview |

No new UI library, global layout, theme, navigation model or shared-component breaking change is introduced. HR-only responsive CSS is scoped with `hr-` classes and follows existing mobile breakpoints.
