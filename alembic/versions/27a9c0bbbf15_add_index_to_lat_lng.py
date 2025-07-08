"""add index to lat_lng

Revision ID: 27a9c0bbbf15
Revises: 93aad4dcb7a6
Create Date: 2025-05-07 04:21:14.864191

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '27a9c0bbbf15'
down_revision: str | None = '93aad4dcb7a6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index('idx_lat_lng', 'land_listing', ['lat', 'lng'])


def downgrade() -> None:
    op.drop_index('idx_lat_lng', table_name='land_listing')
