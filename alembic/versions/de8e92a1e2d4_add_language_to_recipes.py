"""add language to recipes

Revision ID: de8e92a1e2d4
Revises: bf3416c9653d
Create Date: 2026-10-06 22:05:06.051106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de8e92a1e2d4'
down_revision: Union[str, Sequence[str], None] = 'bf3416c9653d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE recipes ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'English'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE recipes DROP COLUMN IF EXISTS language")
