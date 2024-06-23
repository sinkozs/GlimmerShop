from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import Product, User, Category, ProductCategory, Cart, CartItem
from schemas.schemas import CartItemUpdate
from sqlalchemy.orm import selectinload, joinedload

from exceptions.product_exceptions import ProductException
from exceptions.cart_exceptions import CartException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict
from typing import List


class CartService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_and_cart_by_user_id(self, user_id: UUID) -> User:
        try:
            stmt = select(User).options(selectinload(User.cart)).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalars().one_or_none()

            if not user:
                raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"User with id {user_id} not found!")
            return user
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_cart_item(self, user_cart_id: int, product_id: int) -> CartItem:
        try:
            stmt = select(CartItem).where(CartItem.cart_id == user_cart_id,
                                          CartItem.product_id == product_id)
            cart_item_result = await self.db.execute(stmt)
            existing_cart_item = cart_item_result.scalars().one_or_none()

            if not existing_cart_item:
                raise CartException(status_code=status.HTTP_404_NOT_FOUND,
                                               detail=f"Cart item not found!")
            return existing_cart_item
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_all_cart_item_by_user_id(self, user_id: UUID) -> list:
        try:
            user = await self.get_user_and_cart_by_user_id(user_id)
            stmt = select(CartItem).options(selectinload(CartItem.cart)).where(CartItem.cart_id == user.cart.id)
            cart_item_result = await self.db.execute(stmt)
            cart_items = cart_item_result.scalars().all()

            if not cart_items:
                raise CartException(status_code=status.HTTP_404_NOT_FOUND,

                                               detail=f"No cart items not found!")
            return [db_model_to_dict(c) for c in cart_items]
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    def get_detailed_cart_dict(self, cart_items: List):
        cart_dict = dict()
        total_sum_price = 0
        for item in cart_items:
            product_id = item["product_id"]
            product_name = item["product_name"]
            product_quantity = item["product_quantity"]
            total_product_price = item["total_product_price"]

            if product_id in cart_dict.keys():
                cart_dict[product_id]["product_quantity"] += product_quantity
                cart_dict[product_id]["total_product_price"] += total_product_price

            else:
                cart_dict[product_id] = {"product_name": product_name, "product_quantity": product_quantity,
                                         "total_product_price": total_product_price}

            total_sum_price += total_product_price

        return cart_dict, total_sum_price

    async def get_detailed_user_cart(self, user_id: UUID) -> dict:
        stmt = select(CartItem).options(joinedload(CartItem.product)).join(CartItem.cart).where(Cart.user_id == user_id)
        result = await self.db.execute(stmt)
        cart_items = result.scalars().all()

        details = list()
        for cart_item in cart_items:
            item_detail = {
                "product_id": cart_item.product.id,
                "product_name": cart_item.product.name,
                "product_quantity": cart_item.quantity,
                "total_product_price": cart_item.product.price * cart_item.quantity
            }
            details.append(item_detail)
        cart_dict, total_price = self.get_detailed_cart_dict(details)
        return {"cart_dict": cart_dict, "total_price": total_price}

    async def add_new_item_to_cart(self, user_id: UUID, cart_item: CartItemUpdate):
        try:
            user = await self.get_user_and_cart_by_user_id(user_id)

            stmt = select(Product).filter(Product.id == cart_item.product_id)
            result = await self.db.execute(stmt)
            product: Product = result.scalars().first()

            if not product:
                raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                       detail=f"Product with id {cart_item.product_id} not found!")

            # check if the cart item already exists
            existing_cart_item = await self.get_cart_item(user.cart.id, cart_item.product_id)

            if existing_cart_item:
                existing_cart_item.quantity += cart_item.quantity
            else:
                new_cart_item = CartItem(cart_id=user.cart.id, product_id=cart_item.product_id,
                                         quantity=cart_item.quantity)
                self.db.add(new_cart_item)
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def delete_item_from_cart(self, user_id: UUID, cart_item: CartItemUpdate):
        try:
            user = await self.get_user_and_cart_by_user_id(user_id)
            existing_cart_item = await self.get_cart_item(user.cart.id, cart_item.product_id)

            if existing_cart_item:
                existing_cart_item.quantity -= cart_item.quantity
            else:
                raise CartException(status_code=status.HTTP_404_NOT_FOUND,
                                               detail=f"Cart item not found!")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    # async def delete_everything_from_user_cart(self, user_id: UUID):
    #     try:
    #         user = await self.get_user_and_cart_by_user_id(user_id)
    #
    #         if user.cart.:
    #             existing_cart_item.quantity -= cart_item.quantity
    #         else:
    #             raise CartException(status_code=status.HTTP_404_NOT_FOUND,
    #                                            detail=f"Cart item not found!")
    #     except SQLAlchemyError as e:
    #         print(f"Database access error: {e}")
    #         raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                                detail="An error occurred when accessing the database!")