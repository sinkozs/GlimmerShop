"""Add more Order fields

Revision ID: 0600b2d15bbf
Revises: 704baff440d8
Create Date: 2025-01-17 14:50:00.430094

"""
from alembic import op
import sqlalchemy as sa

revision = '0600b2d15bbf'
down_revision = '704baff440d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('order', sa.Column('first_address', sa.String(), nullable=False), schema='public')
    op.add_column('order', sa.Column('last_address', sa.String(), nullable=False), schema='public')
    op.add_column('order', sa.Column('phone', sa.String(), nullable=False), schema='public')
    op.add_column('order', sa.Column('email', sa.String(), nullable=False), schema='public')


def downgrade() -> None:
    op.drop_column('order', 'phone', schema='public')
    op.drop_column('order', 'first_name', schema='public')
    op.drop_column('order', 'last_name', schema='public')
    op.drop_column('order', 'email', schema='public')
