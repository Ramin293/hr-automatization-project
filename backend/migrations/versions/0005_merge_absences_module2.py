"""Merge the employee-absences and module-2 migration branches.

Revision ID: 0005_merge_absences_module2
Revises: 0004_employee_absences, 0004_module2
Create Date: 2026-07-16
"""

from collections.abc import Sequence

revision: str = "0005_merge_absences_module2"
down_revision: str | Sequence[str] | None = ("0004_employee_absences", "0004_module2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Both parent branches are independent; nothing to reconcile."""


def downgrade() -> None:
    """Splitting the merge point requires no schema changes."""
