import uuid
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(length=200))

    product_category = relationship("ProductCategory", back_populates="category")


class Product(Base):
    __tablename__ = "product"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('public.user.id'))
    name = Column(String(length=100))
    description = Column(String(length=15000))
    price = Column(Integer)
    stock_quantity = Column(Integer)
    material = Column(String(length=100))
    color = Column(String(length=100))
    image_path = Column(String(length=200))
    image_path2 = Column(String(length=200))

    seller = relationship("User", back_populates="product")
    product_category = relationship("ProductCategory", back_populates="product")
    user_orders = relationship("UserOrder", back_populates="product")


class ProductCategory(Base):
    __tablename__ = "product_category"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('public.product.id'))
    category_id = Column(Integer, ForeignKey('public.category.id'))

    product = relationship("Product", back_populates="product_category")
    category = relationship("Category", back_populates="product_category")


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(64), nullable=False)
    is_seller = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)

    product = relationship("Product", back_populates="seller",
                            primaryjoin="and_(User.id==Product.seller_id, User.is_seller==True)")
    cart = relationship("Cart", back_populates="user", uselist=False,
                        primaryjoin="User.id==Cart.user_id")
    user_orders = relationship("UserOrder", back_populates="user", primaryjoin="User.id==UserOrder.user_id")


class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.user.id', ondelete="CASCADE"))

    user = relationship("User", back_populates="cart")
    cart_item = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('public.cart.id'))
    product_id = Column(Integer, ForeignKey('public.product.id'))
    quantity = Column(Integer)

    cart = relationship("Cart", back_populates="cart_item")


class UserOrder(Base):
    __tablename__ = "user_order"
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.user.id'))
    product_id = Column(Integer, ForeignKey('public.product.id'))

    user = relationship("User", back_populates="user_orders")
    product = relationship("Product", back_populates="user_orders")
