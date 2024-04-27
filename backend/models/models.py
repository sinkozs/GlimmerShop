import uuid
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from models.database import Base


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=200))

    event_category = relationship("EventCategory", back_populates="category")


class Organizer(Base):
    __tablename__ = "organizer"
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(64), nullable=False)
    is_organizer = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)

    event = relationship("Event", back_populates="organizer")


class Event(Base):
    __tablename__ = "event"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey('public.organizer.id'))
    title = Column(String(length=100))
    event_description = Column(String(length=15000))
    event_date = Column(DateTime)
    duration = Column(String(length=100))
    location = Column(String(length=200))
    image_path = Column(String(length=200))
    image_path2 = Column(String(length=200))

    organizer = relationship("Organizer", back_populates="event")
    event_category = relationship("EventCategory", back_populates="event")
    user_event = relationship("UserEvent", back_populates="event")
    ticket_type = relationship("TicketType", back_populates="event")


class EventCategory(Base):
    __tablename__ = "event_category"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('public.event.id'))
    category_id = Column(Integer, ForeignKey('public.category.id'))

    event = relationship("Event", back_populates="event_category")
    category = relationship("Category", back_populates="event_category")


class TicketType(Base):
    __tablename__ = "ticket_type"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('public.event.id'))
    title = Column(String(length=100))
    ticket_description = Column(String(length=200))
    price = Column(Integer)
    limits = Column(Integer)
    tickets_sold = Column(Integer, default=0)

    event = relationship("Event", back_populates="ticket_type")


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(64), nullable=False)
    is_organizer = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)

    user_event = relationship("UserEvent", back_populates="user")
    cart = relationship("Cart", back_populates="user")


class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.user.id'))

    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    cart_id = Column(Integer, ForeignKey('public.cart.id'))
    ticket_type_id = Column(Integer, ForeignKey('public.ticket_type.id'))

    cart = relationship("Cart", back_populates="cart_item")


class UserEvent(Base):
    __tablename__ = "user_event"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.user.id'))
    event_id = Column(Integer, ForeignKey('public.event.id'))

    user = relationship("User", back_populates="user_event")
    event = relationship("Event", back_populates="user_event")
    
