"""add_avatar_to_users

Revision ID: b1c660b4cf28
Revises: 9c0a55734e12
Create Date: 2026-10-01 23:52:44.846384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c660b4cf28'
down_revision: Union[str, Sequence[str], None] = '9c0a55734e12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('avatar', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'avatar')
