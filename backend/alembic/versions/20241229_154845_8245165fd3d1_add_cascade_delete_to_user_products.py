"""add_cascade_delete_to_user_products

Revision ID: 8245165fd3d1
Revises: 6fd28514430a
Create Date: 2024-12-29 15:48:45.219325

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8245165fd3d1'
down_revision = '6fd28514430a'
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
