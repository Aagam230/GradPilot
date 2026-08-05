"""program resolution and structured requirements

Revision ID: c31a7e42f9b1
Revises: e98e8ac7efec
Create Date: 2026-08-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c31a7e42f9b1'
down_revision: Union[str, Sequence[str], None] = 'e98e8ac7efec'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('programs', sa.Column('official_domain', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('structured_requirements', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('programs', 'structured_requirements')
    op.drop_column('programs', 'official_domain')
