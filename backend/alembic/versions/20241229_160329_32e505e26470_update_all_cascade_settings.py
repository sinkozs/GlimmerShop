"""update_all_cascade_settings

Revision ID: 32e505e26470
Revises: 5273b95fbe84
Create Date: 2024-12-29 16:03:29.401671

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "32e505e26470"
down_revision = "5273b95fbe84"
branch_labels = None
depends_on = None


def upgrade():
    # Update CartItem foreign keys
    op.drop_constraint(
        "cart_item_cart_id_fkey", "cart_item", schema="public", type_="foreignkey"
    )
    op.drop_constraint(
        "cart_item_product_id_fkey", "cart_item", schema="public", type_="foreignkey"
    )
    op.create_foreign_key(
        "cart_item_cart_id_fkey",
        "cart_item",
        "cart",
        ["cart_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "cart_item_product_id_fkey",
        "cart_item",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )

    # Update ProductCategory foreign key
    op.drop_constraint(
        "product_category_product_id_fkey",
        "product_category",
        schema="public",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "product_category_product_id_fkey",
        "product_category",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )

    # Update UserOrder foreign keys
    op.drop_constraint(
        "user_order_product_id_fkey", "user_order", schema="public", type_="foreignkey"
    )
    op.drop_constraint(
        "user_order_user_id_fkey", "user_order", schema="public", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_order_product_id_fkey",
        "user_order",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_order_user_id_fkey",
        "user_order",
        "user",
        ["user_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )


def downgrade():
    # Revert CartItem foreign keys
    op.drop_constraint(
        "cart_item_cart_id_fkey", "cart_item", schema="public", type_="foreignkey"
    )
    op.drop_constraint(
        "cart_item_product_id_fkey", "cart_item", schema="public", type_="foreignkey"
    )
    op.create_foreign_key(
        "cart_item_cart_id_fkey",
        "cart_item",
        "cart",
        ["cart_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        "cart_item_product_id_fkey",
        "cart_item",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )

    # Revert ProductCategory foreign key
    op.drop_constraint(
        "product_category_product_id_fkey",
        "product_category",
        schema="public",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "product_category_product_id_fkey",
        "product_category",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )

    # Revert UserOrder foreign keys
    op.drop_constraint(
        "user_order_product_id_fkey", "user_order", schema="public", type_="foreignkey"
    )
    op.drop_constraint(
        "user_order_user_id_fkey", "user_order", schema="public", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_order_product_id_fkey",
        "user_order",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        "user_order_user_id_fkey",
        "user_order",
        "user",
        ["user_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
