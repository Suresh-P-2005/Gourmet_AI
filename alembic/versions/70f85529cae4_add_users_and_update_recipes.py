"""add_users_and_update_recipes

Revision ID: 70f85529cae4
Revises: 653d2ac2f567
Create Date: 2026-10-01 16:58:47.358137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70f85529cae4'
down_revision: Union[str, Sequence[str], None] = '653d2ac2f567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    op.execute('ALTER TABLE recipes ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE')
    op.execute('ALTER TABLE recipes ADD COLUMN cuisine_type VARCHAR(50)')
    op.execute('ALTER TABLE recipes ADD COLUMN is_public BOOLEAN DEFAULT FALSE')
    op.execute('ALTER TABLE recipes ADD COLUMN personal_notes TEXT')
    op.execute('''
        CREATE TABLE saved_recipes (
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
            saved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id)
        )
    ''')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TABLE saved_recipes')
    op.execute('ALTER TABLE recipes DROP COLUMN user_id')
    op.execute('ALTER TABLE recipes DROP COLUMN cuisine_type')
    op.execute('ALTER TABLE recipes DROP COLUMN is_public')
    op.execute('ALTER TABLE recipes DROP COLUMN personal_notes')
    op.execute('DROP TABLE users')
