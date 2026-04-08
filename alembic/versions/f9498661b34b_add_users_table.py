"""Add users table

Revision ID: f9498661b34b
Revises: 
Create Date: 2026-04-08 18:06:49.347523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9498661b34b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute("""
                CREATE TABLE users(
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                user_name TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'user' CHECK (role IN ('user', 'radiologist', 'admin','expert')),
                joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
""")


def downgrade() -> None:
    op.execute('DROP TABLE users;')
