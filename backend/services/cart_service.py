from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, Response
import redis.asyncio as aioredis
from models.models import User, Cart, CartItem
from schemas.schemas import CartItemUpdate
from sqlalchemy.orm import selectinload, joinedload

from exceptions.product_exceptions import ProductException
from exceptions.cart_exceptions import CartException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict
from typing import List, Optional


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

    async def get_cart_item(self, user_cart_id: int, product_id: int):
        try:
            stmt = select(CartItem).where(CartItem.cart_id == user_cart_id,
                                          CartItem.product_id == product_id)
            cart_item_result = await self.db.execute(stmt)
            return cart_item_result.scalars().one_or_none()

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

    async def get_detailed_cart_from_db(self, user_id: UUID) -> dict:
        try:
            stmt = select(CartItem).options(joinedload(CartItem.product)).join(CartItem.cart).where(
                Cart.user_id == user_id)
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
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_detailed_cart_from_redis(self, redis: aioredis.Redis, session_id: str) -> List[dict]:
        try:
            cart_key = f"cart:{session_id}"
            cart_items = await redis.hgetall(cart_key)
            return [{"product_id": int(product_id), "quantity": int(quantity)} for product_id, quantity in
                    cart_items.items()]
        except Exception as e:
            print(f"Redis access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the Redis database!")

    async def add_new_item_to_cart(self, cart_item: CartItemUpdate, response: Response, redis: aioredis.Redis,
                                   user_id: Optional[UUID] = None, session_id: Optional[str] = None):
        if user_id:
            user = await self.get_user_and_cart_by_user_id(user_id)
            if not user:
                raise ProductException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

            existing_cart_item = await self.get_cart_item(user.cart.id, cart_item.product_id)

            if existing_cart_item:
                existing_cart_item.quantity += cart_item.quantity
            else:
                new_cart_item = CartItem(cart_id=user.cart.id, product_id=cart_item.product_id,
                                         quantity=cart_item.quantity)
                self.db.add(new_cart_item)
            await self.db.commit()
        else:
            cart_key = f"cart:{session_id}"

            existing_cart_items = await redis.hgetall(cart_key)

            if str(cart_item.product_id) in existing_cart_items:
                existing_quantity = int(existing_cart_items[str(cart_item.product_id)])
                new_quantity = existing_quantity + cart_item.quantity
                await redis.hset(cart_key, str(cart_item.product_id), new_quantity)
            else:
                await redis.hset(cart_key, str(cart_item.product_id), cart_item.quantity)

    async def delete_item_from_cart(self, cart_item: CartItemUpdate, response: Response, redis: aioredis.Redis,
                                    user_id: Optional[UUID] = None, session_id: Optional[str] = None):
        try:
            if user_id:
                user = await self.get_user_and_cart_by_user_id(user_id)
                print(f"User: {db_model_to_dict(user)}")
                if not user:
                    raise ProductException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

                existing_cart_item = await self.get_cart_item(user.cart.id, cart_item.product_id)

                if existing_cart_item:
                    if existing_cart_item.quantity - cart_item.quantity < 0:
                        raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"Negative quantity is not allowed!")
                    else:
                        existing_cart_item.quantity -= cart_item.quantity
                        await self.db.commit()
            else:
                cart_key = f"cart:{session_id}"

                existing_cart_items = await redis.hgetall(cart_key)

                if str(cart_item.product_id) in existing_cart_items:
                    existing_quantity = int(existing_cart_items[str(cart_item.product_id)])
                    if 0 <= existing_quantity - cart_item.quantity:
                        new_quantity = existing_quantity - cart_item.quantity
                    else:
                        raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"Negative quantity is not allowed!")
                    await redis.hset(cart_key, str(cart_item.product_id), new_quantity)
                else:
                    raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"There are no product with id {str(cart_item.product_id)} in the cart!")
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
