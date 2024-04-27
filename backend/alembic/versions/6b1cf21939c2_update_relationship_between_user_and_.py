"""update relationship between User and Cart tables

Revision ID: 6b1cf21939c2
Revises: a585b4277fe3
Create Date: 2024-04-27 22:43:16.738321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b1cf21939c2'
down_revision = 'a585b4277fe3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('cart_user_id_fkey', 'cart', type_='foreignkey')
    op.create_foreign_key(None, 'cart', 'user', ['user_id'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('cart_item_cart_id_fkey', 'cart_item', type_='foreignkey')
    op.drop_constraint('cart_item_ticket_type_id_fkey', 'cart_item', type_='foreignkey')
    op.create_foreign_key(None, 'cart_item', 'ticket_type', ['ticket_type_id'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'cart_item', 'cart', ['cart_id'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('event_organizer_id_fkey', 'event', type_='foreignkey')
    op.create_foreign_key(None, 'event', 'organizer', ['organizer_id'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('event_category_category_id_fkey', 'event_category', type_='foreignkey')
    op.drop_constraint('event_category_event_id_fkey', 'event_category', type_='foreignkey')
    op.create_foreign_key(None, 'event_category', 'event', ['event_id'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'event_category', 'category', ['category_id'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('ticket_type_event_id_fkey', 'ticket_type', type_='foreignkey')
    op.create_foreign_key(None, 'ticket_type', 'event', ['event_id'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('user_event_user_id_fkey', 'user_event', type_='foreignkey')
    op.drop_constraint('user_event_event_id_fkey', 'user_event', type_='foreignkey')
    op.create_foreign_key(None, 'user_event', 'user', ['user_id'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'user_event', 'event', ['event_id'], ['id'], source_schema='public', referent_schema='public')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_event', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'user_event', schema='public', type_='foreignkey')
    op.create_foreign_key('user_event_event_id_fkey', 'user_event', 'event', ['event_id'], ['id'])
    op.create_foreign_key('user_event_user_id_fkey', 'user_event', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'ticket_type', schema='public', type_='foreignkey')
    op.create_foreign_key('ticket_type_event_id_fkey', 'ticket_type', 'event', ['event_id'], ['id'])
    op.drop_constraint(None, 'event_category', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'event_category', schema='public', type_='foreignkey')
    op.create_foreign_key('event_category_event_id_fkey', 'event_category', 'event', ['event_id'], ['id'])
    op.create_foreign_key('event_category_category_id_fkey', 'event_category', 'category', ['category_id'], ['id'])
    op.drop_constraint(None, 'event', schema='public', type_='foreignkey')
    op.create_foreign_key('event_organizer_id_fkey', 'event', 'organizer', ['organizer_id'], ['id'])
    op.drop_constraint(None, 'cart_item', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'cart_item', schema='public', type_='foreignkey')
    op.create_foreign_key('cart_item_ticket_type_id_fkey', 'cart_item', 'ticket_type', ['ticket_type_id'], ['id'])
    op.create_foreign_key('cart_item_cart_id_fkey', 'cart_item', 'cart', ['cart_id'], ['id'])
    op.drop_constraint(None, 'cart', schema='public', type_='foreignkey')
    op.create_foreign_key('cart_user_id_fkey', 'cart', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
