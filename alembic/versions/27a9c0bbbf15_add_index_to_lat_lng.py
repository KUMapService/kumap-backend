"""add index to lat_lng

Revision ID: 27a9c0bbbf15
Revises: 93aad4dcb7a6
Create Date: 2025-05-07 04:21:14.864191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27a9c0bbbf15'
down_revision: Union[str, None] = '93aad4dcb7a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_lat_lng', 'land_listing', ['lat', 'lng'])


def downgrade() -> None:
    op.drop_index('idx_lat_lng', table_name='land_listing')
