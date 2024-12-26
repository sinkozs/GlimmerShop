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


def get_cart_service(session: AsyncSession = Depends(get_session)) -> CartService:
    return CartService(session)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


def get_product_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    return ProductService(session)


def get_cart_controller(
    cart_service: CartService = Depends(get_cart_service),
    auth_service: AuthService = Depends(get_auth_service),
    product_service: ProductService = Depends(get_product_service),
) -> CartController:
    return CartController(cart_service, auth_service, product_service)


@router.get("")
async def get_all_cart_item_by_user_id(
    current_user: dict = Depends(get_current_user),
    controller: CartController = Depends(get_cart_controller),
):
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
    current_user: Optional[dict] = Depends(get_current_user),
    controller: CartController = Depends(get_cart_controller),
    redis: aioredis.Redis = Depends(get_redis),
):
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
    controller: CartController = Depends(get_cart_controller),
    redis: aioredis.Redis = Depends(get_redis),
):
    user_id: Optional[UUID] = current_user.get("id") if current_user else None
    session_id = request.cookies.get("session_id") if not user_id else None
    print(f"session_id: {session_id}")

    return await controller.add_new_item_to_cart(
        new_cart_item=cart_item,
        response=response,
        redis=redis,
        user_id=user_id,
        session_id=session_id,
    )


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
