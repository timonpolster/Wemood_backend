"""Initial migration - create articles table

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('ai_analysis', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_articles'))
    )
    
    # Create indexes
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=False)
    op.create_index(op.f('ix_articles_title'), 'articles', ['title'], unique=False)
    
    # Create GIN index for JSONB ai_analysis column (for fast tag searching)
    op.create_index(
        'ix_articles_ai_analysis_gin',
        'articles',
        ['ai_analysis'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    op.drop_index('ix_articles_ai_analysis_gin', table_name='articles', postgresql_using='gin')
    op.drop_index(op.f('ix_articles_title'), table_name='articles')
    op.drop_index(op.f('ix_articles_id'), table_name='articles')
    op.drop_table('articles')
