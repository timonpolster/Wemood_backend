"""Add sources list, literature, fazit, videos fields to articles

Revision ID: 004_add_chapter_fields
Revises: 003_add_fulltext_search
Create Date: 2026-03-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_add_chapter_fields'
down_revision: Union[str, None] = '003_add_fulltext_search'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'articles',
        sa.Column(
            'sources',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='[]',
            nullable=True,
            comment='Liste der Quellen des Artikels.'
        )
    )

    op.execute("""
               UPDATE articles
               SET sources = CASE
                                 WHEN source IS NOT NULL AND source != ''
            THEN jsonb_build_array(source)
                                 ELSE '[]'::jsonb
                   END
               """)

    op.drop_column('articles', 'source')

    op.add_column(
        'articles',
        sa.Column(
            'literature',
            sa.Text(),
            nullable=True,
            comment='Weiterführende Literatur zum Artikel.'
        )
    )

    op.add_column(
        'articles',
        sa.Column(
            'fazit',
            sa.Text(),
            nullable=True,
            comment='Fazit bzw. Schlussfolgerung des Artikels.'
        )
    )

    op.add_column(
        'articles',
        sa.Column(
            'videos',
            sa.Text(),
            nullable=True,
            comment='Zugehörige Video-Links (z.B. YouTube-URLs), zeilenweise getrennt.'
        )
    )


def downgrade() -> None:
    op.add_column(
        'articles',
        sa.Column('source', sa.String(length=255), nullable=True)
    )

    op.execute("""
               UPDATE articles
               SET source = CASE
                                WHEN sources IS NOT NULL AND jsonb_array_length(sources) > 0
                                    THEN sources->>0
                                ELSE NULL
                   END
               """)

    op.drop_column('articles', 'sources')
    op.drop_column('articles', 'videos')
    op.drop_column('articles', 'fazit')
    op.drop_column('articles', 'literature')