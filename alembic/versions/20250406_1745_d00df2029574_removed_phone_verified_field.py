"""Removed phone_verified field'

Revision ID: d00df2029574
Revises: 771c35b1dfc9
Create Date: 2025-04-06 17:45:02.690213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd00df2029574'
down_revision: Union[str, None] = '771c35b1dfc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'phone_verified')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('phone_verified', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
