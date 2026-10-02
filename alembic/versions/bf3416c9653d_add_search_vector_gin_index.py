"""add_search_vector_gin_index

Revision ID: bf3416c9653d
Revises: 7e5420600b2c
Create Date: 2026-10-02 12:55:40.919635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf3416c9653d'
down_revision: Union[str, Sequence[str], None] = '7e5420600b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE recipes ADD COLUMN search_vector tsvector")
    op.execute("CREATE INDEX idx_recipes_search_vector ON recipes USING GIN(search_vector)")
    
    # Create function to update search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION recipes_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.ingredients::text, '')), 'B');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON recipes FOR EACH ROW EXECUTE PROCEDURE recipes_search_vector_update();
    """)
    
    # Update existing rows
    op.execute("UPDATE recipes SET id = id")

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON recipes")
    op.execute("DROP FUNCTION IF EXISTS recipes_search_vector_update()")
    op.execute("DROP INDEX IF EXISTS idx_recipes_search_vector")
    op.execute("ALTER TABLE recipes DROP COLUMN IF EXISTS search_vector")
