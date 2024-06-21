from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import Product, User, Category, ProductCategory, Cart, CartItem
from schemas.schemas import CartItemCreate
from sqlalchemy.orm import joinedload, selectinload

from .product_service import ProductService
from exceptions.category_exceptions import CategoryException
from exceptions.product_exceptions import ProductException
from exceptions.cart_exceptions import CartException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict, dict_to_db_model, convert_str_to_int_if_numeric


class CartService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def add_new_item_to_cart(self, user_id: UUID, cart_item: CartItemCreate):
        try:
            async with self.db.begin():
                stmt = select(User).options(selectinload(User.cart)).where(User.id == user_id)
                result = await self.db.execute(stmt)
                user = result.scalars().one_or_none()

                if not user:
                    raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"User with id {user_id} not found!")

                stmt = select(Product).filter(Product.id == cart_item.product_id)
                result = await self.db.execute(stmt)
                product: Product = result.scalars().first()

                if not product:
                    raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"Product with id {cart_item.product_id} not found!")

                # check if the cart item already exists
                cart_item_stmt = select(CartItem).where(CartItem.cart_id == user.cart.id,
                                                        CartItem.product_id == cart_item.product_id)
                cart_item_result = await self.db.execute(cart_item_stmt)
                existing_cart_item = cart_item_result.scalars().one_or_none()

                if existing_cart_item:
                    existing_cart_item.quantity += cart_item.quantity
                else:
                    new_cart_item = CartItem(cart_id=user.cart.id, product_id=cart_item.product_id,
                                             quantity=cart_item.quantity)
                    self.db.add(new_cart_item)
                    await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CartException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")
