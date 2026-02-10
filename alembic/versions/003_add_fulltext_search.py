"""Add Full text Search index for hybrid search

Revision ID: 003_add_fulltext_search
Revises: 002_create_users
Create Date: 2026-02-10

"""
from typing import Sequence, Union
from alembic import op

revision: str = '003_add_fulltext_search'
down_revision: Union[str, None] = '002_create_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_articles_fulltext_search 
        ON articles 
        USING GIN (
            (
                setweight(to_tsvector('german', COALESCE(title, '')), 'A') ||
                setweight(to_tsvector('german', COALESCE(content, '')), 'B')
            )
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_articles_summary_fulltext
        ON articles
        USING GIN (
            to_tsvector('german', COALESCE(ai_analysis->>'summary', ''))
        )
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_articles_fulltext_search")
    op.execute("DROP INDEX IF EXISTS ix_articles_summary_fulltext")
