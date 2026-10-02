"""convert_to_jsonb

Revision ID: 7e5420600b2c
Revises: b1c660b4cf28
Create Date: 2026-10-02 12:48:56.771085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e5420600b2c'
down_revision: Union[str, Sequence[str], None] = 'b1c660b4cf28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE recipes ALTER COLUMN ingredients DROP DEFAULT")
    op.execute("ALTER TABLE recipes ALTER COLUMN instructions DROP DEFAULT")
    op.execute("ALTER TABLE recipes ALTER COLUMN nutrition DROP DEFAULT")
    
    op.execute("ALTER TABLE recipes ALTER COLUMN ingredients TYPE JSONB USING ingredients::JSONB")
    op.execute("ALTER TABLE recipes ALTER COLUMN instructions TYPE JSONB USING instructions::JSONB")
    op.execute("ALTER TABLE recipes ALTER COLUMN nutrition TYPE JSONB USING nutrition::JSONB")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE recipes ALTER COLUMN ingredients TYPE TEXT USING ingredients::TEXT")
    op.execute("ALTER TABLE recipes ALTER COLUMN instructions TYPE TEXT USING instructions::TEXT")
    op.execute("ALTER TABLE recipes ALTER COLUMN nutrition TYPE TEXT USING nutrition::TEXT")
