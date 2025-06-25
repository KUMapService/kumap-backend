"""add index on region_coordinate (lat, lng, type)

Revision ID: 40a1c80ef2f9
Revises: 45443fb76a87
Create Date: 2025-06-25 08:54:04.608392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40a1c80ef2f9'
down_revision: Union[str, None] = '45443fb76a87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index(
        'idx_region_coordinate_lat_lng_type',
        'region_coordinate',
        ['lat', 'lng', 'type']
    )


def downgrade():
    op.drop_index('idx_region_coordinate_lat_lng_type', table_name='region_coordinate')
