"""init models

Revision ID: b5ded1daf1ab
Revises: d3f9f2c34284
Create Date: 2026-05-11 11:01:30.126367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5ded1daf1ab'
down_revision: Union[str, Sequence[str], None] = 'd3f9f2c34284'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
