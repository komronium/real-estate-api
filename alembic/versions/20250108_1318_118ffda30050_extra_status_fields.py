"""Extra status fields

Revision ID: 118ffda30050
Revises: 1f551c1ab7ad
Create Date: 2025-01-08 13:18:17.913272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '118ffda30050'
down_revision: Union[str, None] = '1f551c1ab7ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('user', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.drop_column('user', 'profile_image')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_image', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.alter_column('user', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('user', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
