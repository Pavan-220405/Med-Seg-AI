"""Add models table

Revision ID: 3ed801c50d72
Revises: f9498661b34b
Create Date: 2026-04-08 18:25:40.575957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ed801c50d72'
down_revision: Union[str, None] = 'f9498661b34b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute("""
                CREATE TABLE models(
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    description TEXT,
                    framework TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    added_by UUID REFERENCES users(id) ON DELETE SET NULL,
               
                    UNIQUE(model_name, version)
                );
            """)


def downgrade() -> None:
    op.execute('DROP TABLE models;')