"""historical applications

Revision ID: 6e3b6d6f5875
Revises: a695242f983c
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '6e3b6d6f5875'
down_revision: Union[str, Sequence[str], None] = 'c31a7e42f9b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'historical_applications' not in inspector.get_table_names():
        op.create_table(
            'historical_applications',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('canonical_university', sa.String(), nullable=False),
            sa.Column('canonical_program', sa.String(), nullable=False),
            sa.Column('application_year', sa.Integer(), nullable=True),
            sa.Column('decision', sa.String(), nullable=False),
            sa.Column('gpa_value', sa.Float(), nullable=True),
            sa.Column('gpa_scale', sa.Float(), nullable=True),
            sa.Column('gpa_normalized', sa.Float(), nullable=True),
            sa.Column('gre_total', sa.Integer(), nullable=True),
            sa.Column('gre_quant', sa.Integer(), nullable=True),
            sa.Column('gre_verbal', sa.Integer(), nullable=True),
            sa.Column('toefl', sa.Integer(), nullable=True),
            sa.Column('ielts', sa.Float(), nullable=True),
            sa.Column('undergraduate_major', sa.String(), nullable=True),
            sa.Column('undergraduate_country', sa.String(), nullable=True),
            sa.Column('research_experience', sa.Boolean(), nullable=True),
            sa.Column('publication_count', sa.Integer(), nullable=True),
            sa.Column('work_experience_months', sa.Integer(), nullable=True),
            sa.Column('source_type', sa.String(), nullable=False),
            sa.Column('source_url', sa.String(), nullable=True),
            sa.Column('data_quality_score', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_historical_applications_canonical_program', 'historical_applications', ['canonical_program'])
        op.create_index('ix_historical_applications_canonical_university', 'historical_applications', ['canonical_university'])


def downgrade() -> None:
    bind = op.get_bind()
    if 'historical_applications' in sa.inspect(bind).get_table_names():
        op.drop_table('historical_applications')
