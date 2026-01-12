"""fix gold requests and user

Revision ID: 6309d6791297
Revises: ac375096c3e4
Create Date: 2026-01-12 18:50:23.391812

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6309d6791297"
down_revision: Union[str, None] = "ac375096c3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint(
        "gold_verification_requests_requested_by_fkey",
        "gold_verification_requests",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "gold_verification_requests_requested_by_fkey",
        "gold_verification_requests",
        "user",
        ["requested_by"],
        ["id"],
        ondelete="CASCADE",
    )
