"""update order and order items models

Revision ID: 40d2b47877b4
Revises: 2ad8e533e188
Create Date: 2025-01-14 21:17:16.769862
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '40d2b47877b4'
down_revision = '2ad8e533e188'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old userorders table if it exists
    op.execute('DROP TABLE IF EXISTS public.userorders CASCADE')

    # Create new order table
    op.create_table('order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('status', sa.String(), nullable=False, server_default='completed'),
        sa.Column('shipping_address', sa.String(), nullable=True),
        sa.Column('tracking_number', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['public.user.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_order_id'), 'order', ['id'], unique=False, schema='public')

    # Create new order_item table
    op.create_table('order_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('price_at_purchase', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['public.order.id']),
        sa.ForeignKeyConstraint(['product_id'], ['public.product.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_order_item_id'), 'order_item', ['id'], unique=False, schema='public')


def downgrade() -> None:
    # Drop new tables
    op.drop_index(op.f('ix_public_order_item_id'), table_name='order_item', schema='public')
    op.drop_table('order_item', schema='public')
    op.drop_index(op.f('ix_public_order_id'), table_name='order', schema='public')
    op.drop_table('order', schema='public')

    # Recreate old user_order table (if needed)
    op.create_table('user_order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['public.user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
