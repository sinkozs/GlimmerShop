"""Remove description column from categories

Revision ID: 8ee29ed8daff
Revises: e4b536a07a41
Create Date: 2024-11-07 20:01:16.037778

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8ee29ed8daff"
down_revision = "e4b536a07a41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("cart_user_id_fkey", "cart", type_="foreignkey")
    op.create_foreign_key(
        None,
        "cart",
        "user",
        ["user_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE",
    )
    op.drop_constraint("cart_item_product_id_fkey", "cart_item", type_="foreignkey")
    op.drop_constraint("cart_item_cart_id_fkey", "cart_item", type_="foreignkey")
    op.create_foreign_key(
        None,
        "cart_item",
        "cart",
        ["cart_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        None,
        "cart_item",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.drop_column("category", "category_description")
    op.drop_constraint("product_seller_id_fkey", "product", type_="foreignkey")
    op.create_foreign_key(
        None,
        "product",
        "user",
        ["seller_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.drop_constraint(
        "product_category_category_id_fkey", "product_category", type_="foreignkey"
    )
    op.drop_constraint(
        "product_category_product_id_fkey", "product_category", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "product_category",
        "category",
        ["category_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        None,
        "product_category",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.drop_constraint("user_order_user_id_fkey", "user_order", type_="foreignkey")
    op.drop_constraint("user_order_product_id_fkey", "user_order", type_="foreignkey")
    op.create_foreign_key(
        None,
        "user_order",
        "user",
        ["user_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    op.create_foreign_key(
        None,
        "user_order",
        "product",
        ["product_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user_order", schema="public", type_="foreignkey")
    op.drop_constraint(None, "user_order", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "user_order_product_id_fkey", "user_order", "product", ["product_id"], ["id"]
    )
    op.create_foreign_key(
        "user_order_user_id_fkey", "user_order", "user", ["user_id"], ["id"]
    )
    op.drop_constraint(None, "product_category", schema="public", type_="foreignkey")
    op.drop_constraint(None, "product_category", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "product_category_product_id_fkey",
        "product_category",
        "product",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "product_category_category_id_fkey",
        "product_category",
        "category",
        ["category_id"],
        ["id"],
    )
    op.drop_constraint(None, "product", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "product_seller_id_fkey", "product", "user", ["seller_id"], ["id"]
    )
    op.add_column(
        "category",
        sa.Column(
            "category_description",
            sa.VARCHAR(length=200),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(None, "cart_item", schema="public", type_="foreignkey")
    op.drop_constraint(None, "cart_item", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "cart_item_cart_id_fkey", "cart_item", "cart", ["cart_id"], ["id"]
    )
    op.create_foreign_key(
        "cart_item_product_id_fkey", "cart_item", "product", ["product_id"], ["id"]
    )
    op.drop_constraint(None, "cart", schema="public", type_="foreignkey")
    op.create_foreign_key(
        "cart_user_id_fkey", "cart", "user", ["user_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###
