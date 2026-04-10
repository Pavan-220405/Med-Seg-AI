"""Add is_active to models

Revision ID: 467ee8a71ab6
Revises: a583cbd34146
Create Date: 2026-04-10 11:57:27.914750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '467ee8a71ab6'
down_revision: Union[str, None] = 'a583cbd34146'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""  
        ALTER TABLE models
        ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE models
        DROP COLUMN is_active;
""")
