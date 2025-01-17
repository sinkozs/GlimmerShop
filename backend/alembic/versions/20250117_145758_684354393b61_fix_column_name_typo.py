"""Fix column name typo

Revision ID: {new_revision_id}  # Alembic will generate this
Revises: 0600b2d15bbf
Create Date: 2025-01-17 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '{new_revision_id}'
down_revision = '0600b2d15bbf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('order', 'first_address', new_column_name='first_name', schema='public')
    op.alter_column('order', 'last_address', new_column_name='last_name', schema='public')


def downgrade() -> None:
    op.alter_column('order', 'first_name', new_column_name='first_address', schema='public')
    op.alter_column('order', 'last_name', new_column_name='last_address', schema='public')
