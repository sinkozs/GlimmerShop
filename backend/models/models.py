import uuid
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from models.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(64), nullable=False)
    is_organiser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)
    user_events = relationship("UserEvents", back_populates="user")


class Organizer(Base):
    __tablename__ = "organizers"
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(64), nullable=False)
    is_organiser = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)
    events = relationship("Events", back_populates="organiser")


class Events(Base):
    __tablename__ = "events"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    organiser_id = Column(Integer, ForeignKey('organisers.id'))
    title = Column(String(length=100))
    event_description = Column(String(length=15000))
    event_date = Column(DateTime)
    duration = Column(String(length=100))
    location = Column(String(length=200))
    image_path = Column(String(length=200))
    image_path2 = Column(String(length=200))

    organiser = relationship("Organiser", back_populates="events")
    event_category = relationship("EventCategory", back_populates="event")
    user_events = relationship("UserEvents", back_populates="event")
    ticket_types = relationship("TicketType", back_populates="event")

    class TicketType(Base):
        __tablename__ = "ticket_types"
        __table_args__ = {'schema': 'public'}
        id = Column(Integer, primary_key=True, index=True)
        event_id = Column(Integer, ForeignKey('events_table.id'))
        title = Column(String(length=100))
        ticket_description = Column(String(length=200))
        price = Column(Integer)
        limits = Column(Integer)
        tickets_sold = Column(Integer, default=0)
        event = relationship("Events", back_populates="ticket_types")


class UserEvents(Base):
    __tablename__ = "user_events"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events_table.id'))

    user = relationship("User", back_populates="user_events")
    event = relationship("Events", back_populates="user_events")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=200))

    event_category = relationship("EventCategory", back_populates="category")


class EventCategory(Base):
    __tablename__ = "event_categories"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events_table.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    event = relationship("Events", back_populates="event_category")
    category = relationship("Category", back_populates="event_category")


class Cart(Base):
    __table_args__ = {'schema': 'public'}
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    ticket_type_id = Column(Integer, ForeignKey('ticket_types.id'))
    cart = relationship("Cart", back_populates="cart_items")

