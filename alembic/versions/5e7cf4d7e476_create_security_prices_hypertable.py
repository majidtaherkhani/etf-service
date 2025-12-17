"""create security_prices hypertable

Revision ID: 5e7cf4d7e476
Revises: 
Create Date: 2025-12-17 00:25:16.644629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e7cf4d7e476'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    
    op.create_table('security_prices',
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('date', 'ticker')
    )
    
    op.create_index('idx_ticker_date', 'security_prices', ['ticker', sa.literal_column('date DESC')], unique=False)
    op.create_index(op.f('ix_security_prices_date'), 'security_prices', ['date'], unique=False)
    op.create_index(op.f('ix_security_prices_ticker'), 'security_prices', ['ticker'], unique=False)
    
    op.execute("SELECT create_hypertable('security_prices', 'date', chunk_time_interval => interval '1 day')")


def downgrade() -> None:
    op.drop_index(op.f('ix_security_prices_ticker'), table_name='security_prices')
    op.drop_index(op.f('ix_security_prices_date'), table_name='security_prices')
    op.drop_index('idx_ticker_date', table_name='security_prices')
    op.drop_table('security_prices')
