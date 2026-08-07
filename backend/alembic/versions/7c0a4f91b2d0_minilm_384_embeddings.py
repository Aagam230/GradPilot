"""switch program chunk embeddings to MiniLM 384 dimensions

Revision ID: 7c0a4f91b2d0
Revises: 6e3b6d6f5875

Existing vectors are cleared because 1536-dimensional OpenAI vectors cannot be converted into
384-dimensional MiniLM vectors. Source chunk text is preserved and will be re-embedded when a
program is rebuilt/retrieved.
"""
from typing import Sequence, Union
from alembic import op

revision: str = '7c0a4f91b2d0'
down_revision: Union[str, Sequence[str], None] = 'a695242f983c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE program_chunks SET embedding = NULL WHERE embedding IS NOT NULL")
    op.execute("ALTER TABLE program_chunks ALTER COLUMN embedding TYPE vector(384) USING NULL::vector(384)")


def downgrade() -> None:
    op.execute("UPDATE program_chunks SET embedding = NULL WHERE embedding IS NOT NULL")
    op.execute("ALTER TABLE program_chunks ALTER COLUMN embedding TYPE vector(1536) USING NULL::vector(1536)")
