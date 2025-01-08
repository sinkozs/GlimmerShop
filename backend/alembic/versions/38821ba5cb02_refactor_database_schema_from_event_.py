"""Refactor database schema from event management to jewelry e-commerce

Revision ID: 38821ba5cb02
Revises: 
Create Date: 2024-06-10 14:42:36.087366

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "38821ba5cb02"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_name", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_category_id"), "category", ["id"], unique=False, schema="public"
    )
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=64), nullable=False),
        sa.Column("is_seller", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("registration_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_user_email"), "user", ["email"], unique=True, schema="public"
    )
    op.create_index(
        op.f("ix_public_user_id"), "user", ["id"], unique=False, schema="public"
    )
    op.create_table(
        "cart",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["public.user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_cart_id"), "cart", ["id"], unique=False, schema="public"
    )
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=15000), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=True),
        sa.Column("material", sa.String(length=100), nullable=True),
        sa.Column("color", sa.String(length=100), nullable=True),
        sa.Column("image_path", sa.String(length=200), nullable=True),
        sa.Column("image_path2", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["public.user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_product_id"), "product", ["id"], unique=False, schema="public"
    )
    op.create_table(
        "cart_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cart_id"],
            ["public.cart.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["public.product.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_cart_item_id"),
        "cart_item",
        ["id"],
        unique=False,
        schema="public",
    )
    op.create_table(
        "product_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["public.category.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["public.product.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_product_category_id"),
        "product_category",
        ["id"],
        unique=False,
        schema="public",
    )
    op.create_table(
        "user_order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["public.product.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["public.user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_user_order_id"),
        "user_order",
        ["id"],
        unique=False,
        schema="public",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_public_user_order_id"), table_name="user_order", schema="public"
    )
    op.drop_table("user_order", schema="public")
    op.drop_index(
        op.f("ix_public_product_category_id"),
        table_name="product_category",
        schema="public",
    )
    op.drop_table("product_category", schema="public")
    op.drop_index(
        op.f("ix_public_cart_item_id"), table_name="cart_item", schema="public"
    )
    op.drop_table("cart_item", schema="public")
    op.drop_index(op.f("ix_public_product_id"), table_name="product", schema="public")
    op.drop_table("product", schema="public")
    op.drop_index(op.f("ix_public_cart_id"), table_name="cart", schema="public")
    op.drop_table("cart", schema="public")
    op.drop_index(op.f("ix_public_user_id"), table_name="user", schema="public")
    op.drop_index(op.f("ix_public_user_email"), table_name="user", schema="public")
    op.drop_table("user", schema="public")
    op.drop_index(op.f("ix_public_category_id"), table_name="category", schema="public")
    op.drop_table("category", schema="public")
    # ### end Alembic commands ###
