"""fix one_id_info user fk cascade

Revision ID: ac375096c3e4
Revises: f17e42c8e30d
Create Date: 2026-01-12 18:46:58.695484

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ac375096c3e4"
down_revision: Union[str, None] = "f17e42c8e30d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint(
        "one_id_info_user_id_fkey",
        "one_id_info",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "one_id_info_user_id_fkey",
        "one_id_info",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        "one_id_info_user_id_fkey",
        "one_id_info",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "one_id_info_user_id_fkey",
        "one_id_info",
        "users",
        ["user_id"],
        ["id"],
    )
