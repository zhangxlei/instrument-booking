"""add_price_per_hour

Revision ID: a1b2c3d4e5f6
Revises: 05ba51dd36ff
Create Date: 2026-07-03 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '05ba51dd36ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('instruments',
        sa.Column('price_per_hour', sa.Numeric(10, 2), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('instruments', 'price_per_hour')
