import uuid
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(length=200))

    product_category = relationship("ProductCategory", back_populates="category")


class Product(Base):
    __tablename__ = "product"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(
        UUID(as_uuid=True), ForeignKey("public.user.id", ondelete="CASCADE")
    )
    name = Column(String(length=100))
    description = Column(String(length=15000))
    price = Column(Float)
    stock_quantity = Column(Integer)
    material = Column(String(length=100))
    color = Column(String(length=100))
    image_path = Column(String(length=200))
    image_path2 = Column(String(length=200))

    seller = relationship("User", back_populates="products")
    product_category = relationship(
        "ProductCategory", back_populates="product", cascade="all, delete-orphan"
    )
    order_items = relationship("OrderItem", back_populates="product")


class ProductCategory(Base):
    __tablename__ = "product_category"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("public.product.id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("public.category.id"))

    product = relationship("Product", back_populates="product_category")
    category = relationship("Category", back_populates="product_category")


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50))
    last_name = Column(String(55))
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(128), nullable=False)
    password_length = Column(Integer)
    is_seller = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(Date, nullable=False)

    products = relationship(
        "Product",
        back_populates="seller",
        uselist=True,
        cascade="all, delete-orphan",
        primaryjoin="and_(User.id==Product.seller_id, User.is_seller==True)",
    )
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "order"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.user.id"), nullable=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    shipping_address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    tracking_number = Column(String, nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_item"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("public.order.id"))
    product_id = Column(Integer, ForeignKey("public.product.id"))
    price_at_purchase = Column(Float)
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
