# HR Permission Matrix

| Permission | HR specialist | Manager | Employee | Process admin |
| --- | --- | --- | --- | --- |
| `hr.read` | yes | yes | yes | yes |
| `hr.employee.read.self` | no | yes | yes | no |
| `hr.employee.read.team` | no | yes | no | no |
| `hr.employee.read.all` | yes | no | no | no |
| `hr.employee.write` | yes | no | no | no |
| `hr.compensation.read` | yes | no | no | no |
| `hr.leave.request` | yes | yes | yes | no |
| `hr.leave.approve.manager` | no | yes, direct reports | no | no |
| `hr.leave.approve.hr` | yes | no | no | no |

Permissions grant an action but do not bypass ABAC. HR requests on behalf of an employee are audited through the normal actor context.
