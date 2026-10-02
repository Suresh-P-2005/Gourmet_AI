"""add_is_admin_to_users

Revision ID: 9c0a55734e12
Revises: 77f3bff3b9b6
Create Date: 2026-10-01 21:07:29.730729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c0a55734e12'
down_revision: Union[str, Sequence[str], None] = '77f3bff3b9b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_admin')
