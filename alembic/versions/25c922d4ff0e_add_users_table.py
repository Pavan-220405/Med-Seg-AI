"""Add users table

Revision ID: 25c922d4ff0e
Revises: 
Create Date: 2026-04-06 22:32:11.532769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25c922d4ff0e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute("""
                CREATE TABLE users(
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                user_name TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'user' CHECK (role IN ('user', 'radiologist', 'admin')),
                joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
""")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE users;")
