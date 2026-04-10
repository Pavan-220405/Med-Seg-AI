"""Add metrics to models table

Revision ID: a583cbd34146
Revises: c6031a1ab058
Create Date: 2026-04-10 11:24:40.041878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a583cbd34146'
down_revision: Union[str, None] = 'c6031a1ab058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE models
        ADD COLUMN metrics JSONB DEFAULT '{}';
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE models
        DROP COLUMN metrics;
""")

