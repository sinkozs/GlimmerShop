"""change Price type to Float in the Product table

Revision ID: 704baff440d8
Revises: 40d2b47877b4
Create Date: 2025-01-15 17:19:25.310572
"""
from alembic import op
import sqlalchemy as sa

revision = '704baff440d8'
down_revision = '40d2b47877b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create temporary column
    op.add_column('product',
        sa.Column('price_new', sa.Float(), nullable=True),
        schema='public'
    )

    op.execute('UPDATE public.product SET price_new = price::float')
    op.drop_column('product', 'price', schema='public')

    op.alter_column('product', 'price_new',
        new_column_name='price',
        schema='public'
    )


def downgrade() -> None:
    op.add_column('product',
        sa.Column('price_old', sa.Integer(), nullable=True),
        schema='public'
    )

    # Copy and convert data back to integer
    op.execute('UPDATE public.product SET price_old = price::integer')

    # Drop float column
    op.drop_column('product', 'price', schema='public')

    # Rename back to original
    op.alter_column('product', 'price_old',
        new_column_name='price',
        schema='public'
    )
