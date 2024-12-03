from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Request
import redis.asyncio as aioredis
from dependencies import get_session
from controllers.cart_controller import CartController
from services.cart_service import CartService
from services.auth_service import AuthService
from services.product_service import ProductService
from schemas.schemas import CartItemUpdate
from dependencies import get_current_user
from models.database import get_redis
from exceptions.product_exceptions import ProductException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


router = APIRouter(
    prefix="/cart", tags=["cart"], responses={404: {"Cart": "Not found"}}
)


@router.get("")
async def get_all_cart_item_by_user_id(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CartService(session)
    controller = CartController(service)
    try:
        user_id: UUID = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await controller.get_all_cart_item_by_user_id(user_id)
    except HTTPException as e:
        raise e


@router.get("/user-cart")
async def get_detailed_user_cart(
    request: Request,
    response: Response,
    current_user: Optional[dict] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
):
    service = CartService(session)
    controller = CartController(service)
    auth_service = AuthService(session)
    try:
        user_id: Optional[UUID] = current_user.get("id") if current_user else None

        # Get the session ID for guest users
        session_id = request.cookies.get("session_id")
        if not user_id and not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user or session ID found.",
            )

        return await controller.get_detailed_user_cart(redis, user_id, session_id)
    except HTTPException as e:
        raise e


@router.post("/add")
async def add_new_item_to_cart(
    cart_item: CartItemUpdate,
    request: Request,
    response: Response,
    current_user: Optional[dict] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
):
    service = CartService(session)
    controller = CartController(service)
    auth_service = AuthService(session)
    product_service = ProductService(session)
    try:
        if not await product_service.product_exists(cart_item.product_id):
            raise ProductException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {cart_item.product_id} not fund!",
            )
        user_id: Optional[UUID] = current_user.get("id") if current_user else None
        if user_id:
            user_id = current_user.get("id")
            return await controller.add_new_item_to_cart(
                cart_item, response, redis, user_id
            )

        if not user_id:
            # Get or create session ID for guest users
            session_id = request.cookies.get("session_id")
            if not session_id:
                session_id = await auth_service.create_redis_session(
                    response, redis, user_id
                )
            return await controller.add_new_item_to_cart(
                cart_item, response, redis, None, session_id
            )
    except HTTPException as e:
        raise e


@router.delete("/delete")
async def delete_item_from_cart(
    cart_item: CartItemUpdate,
    request: Request,
    response: Response,
    current_user: Optional[dict] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
):
    service = CartService(session)
    controller = CartController(service)
    product_service = ProductService(session)

    try:
        if not await product_service.product_exists(cart_item.product_id):
            raise ProductException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {cart_item.product_id} not fund!",
            )
        user_id: Optional[UUID] = current_user.get("id") if current_user else None
        if user_id:
            user_id = current_user.get("id")
            return await controller.delete_item_from_cart(
                cart_item, response, redis, user_id, None
            )
        if not user_id:
            session_id = request.cookies.get("session_id")
            return await controller.delete_item_from_cart(
                cart_item, response, redis, None, session_id
            )
    except HTTPException as e:
        raise e
