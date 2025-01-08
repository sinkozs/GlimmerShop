"""check_and_create_tables

Revision ID: c130f2488b63
Revises: d0411898972f
Create Date: 2024-12-29 16:09:01.830749

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c130f2488b63"
down_revision = "d0411898972f"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update Product's seller_id foreign key to cascade from User
    try:
        op.drop_constraint(
            "product_seller_id_fkey", "product", schema="public", type_="foreignkey"
        )
        op.create_foreign_key(
            "product_seller_id_fkey",
            "product",
            "user",
            ["seller_id"],
            ["id"],
            source_schema="public",
            referent_schema="public",
            ondelete="CASCADE",
        )
    except Exception as e:
        print(f"Error updating product seller_id FK: {e}")

    # 2. Update ProductCategory's product_id to cascade from Product
    try:
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
    except Exception as e:
        print(f"Error updating product_category product_id FK: {e}")


def downgrade():
    # Remove CASCADE from Product's seller_id
    try:
        op.drop_constraint(
            "product_seller_id_fkey", "product", schema="public", type_="foreignkey"
        )
        op.create_foreign_key(
            "product_seller_id_fkey",
            "product",
            "user",
            ["seller_id"],
            ["id"],
            source_schema="public",
            referent_schema="public",
        )
    except Exception:
        pass

    # Remove CASCADE from ProductCategory's product_id
    try:
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
    except Exception:
        pass
