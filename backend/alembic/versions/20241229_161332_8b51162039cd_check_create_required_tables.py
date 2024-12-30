"""check_create_required_tables

Revision ID: 8b51162039cd
Revises: c130f2488b63
Create Date: 2024-12-29 16:13:32.339152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b51162039cd'
down_revision = 'c130f2488b63'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names(schema='public')
    print("Existing tables:", existing_tables)

    # Create cart table if it doesn't exist
    if 'cart' not in existing_tables:
        op.create_table('cart',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['public.user.id'], ondelete='CASCADE'),
            schema='public'
        )
        op.create_index(op.f('ix_cart_id'), 'cart', ['id'], unique=False, schema='public')

    # Create cart_item table if it doesn't exist
    if 'cart_item' not in existing_tables:
        op.create_table('cart_item',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('cart_id', sa.Integer(), nullable=True),
            sa.Column('product_id', sa.Integer(), nullable=True),
            sa.Column('quantity', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['cart_id'], ['public.cart.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['product_id'], ['public.product.id'], ondelete='CASCADE'),
            schema='public'
        )
        op.create_index(op.f('ix_cart_item_id'), 'cart_item', ['id'], unique=False, schema='public')

    # Now proceed with updating constraints for existing tables
    if 'product' in existing_tables:
        try:
            op.drop_constraint('product_seller_id_fkey', 'product', schema='public', type_='foreignkey')
            op.create_foreign_key(
                'product_seller_id_fkey',
                'product',
                'user',
                ['seller_id'],
                ['id'],
                source_schema='public',
                referent_schema='public',
                ondelete='CASCADE'
            )
        except Exception as e:
            print(f"Error updating product seller_id FK: {e}")

    if 'product_category' in existing_tables:
        try:
            op.drop_constraint('product_category_product_id_fkey', 'product_category', schema='public', type_='foreignkey')
            op.create_foreign_key(
                'product_category_product_id_fkey',
                'product_category',
                'product',
                ['product_id'],
                ['id'],
                source_schema='public',
                referent_schema='public',
                ondelete='CASCADE'
            )
        except Exception as e:
            print(f"Error updating product_category product_id FK: {e}")

def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names(schema='public')

    if 'cart_item' in existing_tables:
        op.drop_table('cart_item', schema='public')
    if 'cart' in existing_tables:
        op.drop_table('cart', schema='public')

    # Remove CASCADE from existing constraints
    if 'product' in existing_tables:
        try:
            op.drop_constraint('product_seller_id_fkey', 'product', schema='public', type_='foreignkey')
            op.create_foreign_key(
                'product_seller_id_fkey',
                'product',
                'user',
                ['seller_id'],
                ['id'],
                source_schema='public',
                referent_schema='public'
            )
        except Exception:
            pass

    if 'product_category' in existing_tables:
        try:
            op.drop_constraint('product_category_product_id_fkey', 'product_category', schema='public', type_='foreignkey')
            op.create_foreign_key(
                'product_category_product_id_fkey',
                'product_category',
                'product',
                ['product_id'],
                ['id'],
                source_schema='public',
                referent_schema='public'
            )
        except Exception:
            pass

