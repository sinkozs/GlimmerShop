"""initial migration

Revision ID: a585b4277fe3
Revises: 
Create Date: 2024-04-27 18:00:20.520383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a585b4277fe3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_category_id'), 'category', ['id'], unique=False, schema='public')
    op.create_table('organizer',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=64), nullable=False),
    sa.Column('is_organizer', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('registration_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_organizer_email'), 'organizer', ['email'], unique=True, schema='public')
    op.create_index(op.f('ix_public_organizer_id'), 'organizer', ['id'], unique=False, schema='public')
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=64), nullable=False),
    sa.Column('is_organizer', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('registration_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_user_email'), 'user', ['email'], unique=True, schema='public')
    op.create_index(op.f('ix_public_user_id'), 'user', ['id'], unique=False, schema='public')
    op.create_table('cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['public.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_cart_id'), 'cart', ['id'], unique=False, schema='public')
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organizer_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('event_description', sa.String(length=15000), nullable=True),
    sa.Column('event_date', sa.DateTime(), nullable=True),
    sa.Column('duration', sa.String(length=100), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('image_path', sa.String(length=200), nullable=True),
    sa.Column('image_path2', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['organizer_id'], ['public.organizer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_event_id'), 'event', ['id'], unique=False, schema='public')
    op.create_table('event_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['public.category.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['public.event.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_event_category_id'), 'event_category', ['id'], unique=False, schema='public')
    op.create_table('ticket_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('ticket_description', sa.String(length=200), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('limits', sa.Integer(), nullable=True),
    sa.Column('tickets_sold', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['public.event.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_ticket_type_id'), 'ticket_type', ['id'], unique=False, schema='public')
    op.create_table('user_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['public.event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['public.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_user_event_id'), 'user_event', ['id'], unique=False, schema='public')
    op.create_table('cart_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('cart_id', sa.Integer(), nullable=True),
    sa.Column('ticket_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cart_id'], ['public.cart.id'], ),
    sa.ForeignKeyConstraint(['ticket_type_id'], ['public.ticket_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_index(op.f('ix_public_cart_item_id'), 'cart_item', ['id'], unique=False, schema='public')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_public_cart_item_id'), table_name='cart_item', schema='public')
    op.drop_table('cart_item', schema='public')
    op.drop_index(op.f('ix_public_user_event_id'), table_name='user_event', schema='public')
    op.drop_table('user_event', schema='public')
    op.drop_index(op.f('ix_public_ticket_type_id'), table_name='ticket_type', schema='public')
    op.drop_table('ticket_type', schema='public')
    op.drop_index(op.f('ix_public_event_category_id'), table_name='event_category', schema='public')
    op.drop_table('event_category', schema='public')
    op.drop_index(op.f('ix_public_event_id'), table_name='event', schema='public')
    op.drop_table('event', schema='public')
    op.drop_index(op.f('ix_public_cart_id'), table_name='cart', schema='public')
    op.drop_table('cart', schema='public')
    op.drop_index(op.f('ix_public_user_id'), table_name='user', schema='public')
    op.drop_index(op.f('ix_public_user_email'), table_name='user', schema='public')
    op.drop_table('user', schema='public')
    op.drop_index(op.f('ix_public_organizer_id'), table_name='organizer', schema='public')
    op.drop_index(op.f('ix_public_organizer_email'), table_name='organizer', schema='public')
    op.drop_table('organizer', schema='public')
    op.drop_index(op.f('ix_public_category_id'), table_name='category', schema='public')
    op.drop_table('category', schema='public')
    # ### end Alembic commands ###
