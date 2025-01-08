"""Cascade delete product_categories on product deletion

Revision ID: d66181a496bb
Revises: c31893cf2b03
Create Date: 2024-12-29 17:45:54.947414

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d66181a496bb"
down_revision = "c31893cf2b03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
