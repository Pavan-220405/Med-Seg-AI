"""Add predictions table

Revision ID: c6031a1ab058
Revises: 3ed801c50d72
Create Date: 2026-04-09 12:40:29.430006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6031a1ab058'
down_revision: Union[str, None] = '3ed801c50d72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("""
            CREATE TABLE predictions(
               prediction_id UUID PRIMARY KEY,
               user_id UUID NOT NULL,
               model_id UUID NOT NULL,
               input_path TEXT NOT NULL,
               mask_path TEXT NOT NULL,
               inference_time FLOAT NOT NULL,
               created_at TIMESTAMPTZ DEFAULT NOW(),

               FOREIGN KEY (user_id) REFERENCES users(id),
               FOREIGN KEY (model_id) REFERENCES models(id)
            )
    """)

def downgrade() -> None:
    op.execute("DROP TABLE predictions;")