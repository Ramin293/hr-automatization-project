# Permission matrix

| Capability | Secretary | Executive | Employee | Process designer |
| --- | --- | --- | --- | --- |
| Read correspondence | Yes | Yes | Scoped | Read-only |
| Register incoming | Yes | No | No | No |
| Create resolution | No | Yes | No | No |
| Claim and complete tasks | Yes | Yes | Yes | No |
| Edit process definition | No | No | No | Yes |
| View audit | Yes | Yes | Scoped | Yes |

RBAC controls capabilities. ABAC must additionally enforce department, participation, classification, ownership, delegation and acting appointment on the backend. Frontend gates are not security controls.
