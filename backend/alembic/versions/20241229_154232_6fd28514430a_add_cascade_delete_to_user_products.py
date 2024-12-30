"""add_cascade_delete_to_user_products

Revision ID: 6fd28514430a
Revises: 15da73220b7b
Create Date: 2024-12-29 15:42:32.850937

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6fd28514430a'
down_revision = '15da73220b7b'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing foreign key constraint
    op.drop_constraint(
        "product_seller_id_fkey",
        "product",
        schema="public",
        type_="foreignkey"
    )

    # Create the new foreign key constraint with CASCADE
    op.create_foreign_key(
        "product_seller_id_fkey",
        "product",
        "user",
        ["seller_id"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="CASCADE"
    )


def downgrade():
    # Drop the CASCADE foreign key constraint
    op.drop_constraint(
        "product_seller_id_fkey",
        "product",
        schema="public",
        type_="foreignkey"
    )

    # Recreate the original foreign key constraint without CASCADE
    op.create_foreign_key(
        "product_seller_id_fkey",
        "product",
        "user",
        ["seller_id"],
        ["id"],
        source_schema="public",
        referent_schema="public"
    )
