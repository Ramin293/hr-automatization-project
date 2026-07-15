# HR Permissions

The frontend development matrix derives permissions from the current persona. `hr.read` opens the HR workspace; `hr.employees.read` grants the employee directory and Add Employee; `hr.sensitive.read` reveals salary. Backend authorization remains authoritative.

Future service policies distinguish `hr.employee.read.self`, `.team` and `.all`, plus separate personal, compensation and medical grants. Managers receive only the minimum absence/availability projection. Access to personal, medical and compensation data must be audited.
