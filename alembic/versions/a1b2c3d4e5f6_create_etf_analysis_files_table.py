"""create etf_analysis_files table

Revision ID: a1b2c3d4e5f6
Revises: 5e7cf4d7e476
Create Date: 2025-12-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5e7cf4d7e476'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('etf_analysis_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('storage_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_etf_analysis_files_id'), 'etf_analysis_files', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_etf_analysis_files_id'), table_name='etf_analysis_files')
    op.drop_table('etf_analysis_files')
