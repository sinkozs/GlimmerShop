"""modify_product_user_fk_cascade

Revision ID: 6e90f703830d
Revises: 8245165fd3d1
Create Date: 2024-12-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = '6e90f703830d'
down_revision = '8245165fd3d1'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()

    # Using text() for raw SQL
    result = conn.execute(
        text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_schema = 'public' 
            AND table_name = 'product' 
            AND constraint_type = 'FOREIGN KEY' 
            AND constraint_name LIKE '%seller_id%';
        """)
    )

    constraint_name = result.scalar()

    if constraint_name:
        # Drop the existing foreign key constraint
        op.drop_constraint(
            constraint_name,
            "product",
            schema="public",
            type_="foreignkey"
        )

    # Create the new foreign key constraint with CASCADE
    op.create_foreign_key(
        "product_seller_id_fkey",  # new constraint name
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
