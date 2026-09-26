"""create recipes table

Revision ID: 653d2ac2f567
Revises: 
Create Date: 2026-09-26 17:39:03.243024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653d2ac2f567'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE recipes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            cuisine TEXT DEFAULT '',
            dietary TEXT DEFAULT '',
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            notes TEXT DEFAULT '',
            nutrition TEXT DEFAULT '{}',
            suggestions TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS recipes")
