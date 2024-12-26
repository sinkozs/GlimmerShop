from uuid import UUID

from exceptions.product_exceptions import ProductException
from services.cart_service import CartService
from services.auth_service import AuthService
from services.product_service import ProductService
from schemas.schemas import CartItemUpdate
from exceptions.cart_exceptions import CartException
import redis.asyncio as aioredis
from typing import Optional, List
from fastapi import HTTPException, Response, status


class CartController:

    def __init__(
        self,
        service: CartService,
        auth_service: AuthService,
        product_service: ProductService,
    ):
        self._service = service
        self._auth_service = auth_service
        self._product_service = product_service

    async def get_all_cart_item_by_user_id(self, user_id: UUID):
        try:
            return await self._service.get_all_cart_item_by_user_id(user_id)
        except CartException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_detailed_user_cart(
        self, redis: aioredis.Redis, user_id: Optional[UUID], session_id: Optional[str]
    ) -> List[dict]:
        try:
            if user_id:
                return await self._service.get_detailed_cart_from_db(user_id)
            elif session_id:
                return await self._service.get_detailed_cart_from_redis(
                    redis, session_id
                )
            else:
                raise ValueError("Either user_id or session_id must be provided.")
        except CartException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_item_to_cart(
        self,
        new_cart_item: CartItemUpdate,
        response: Response,
        redis: aioredis.Redis,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
    ) -> dict:
        try:
            if not await self._product_service.product_exists(new_cart_item.product_id):
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {new_cart_item.product_id} not found!",
                )

            # Handle guest user session
            if not user_id and not session_id:
                session_id = await self._auth_service.create_redis_session(
                    response, redis, user_id
                )

            return await self._service.add_new_item_to_cart(
                new_cart_item, response, redis, user_id, session_id
            )

        except (CartException, ProductException) as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_item_from_cart(
        self,
        new_cart_item: CartItemUpdate,
        response: Response,
        redis: aioredis.Redis,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
    ):
        try:
            if user_id:
                await self._service.delete_item_from_cart(
                    new_cart_item, response, redis, user_id
                )
            elif session_id:
                await self._service.delete_item_from_cart(
                    new_cart_item, response, redis, None, session_id
                )
        except CartException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
