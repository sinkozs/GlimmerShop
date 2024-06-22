from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from controllers.cart_controller import CartController
from services.cart_service import CartService
from schemas.schemas import CartItemUpdate
from dependencies import get_current_user


from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
    responses={404: {"Cart": "Not found"}}
)


@router.post("/add")
async def add_new_item_to_cart(cart_item: CartItemUpdate, current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = CartService(session)
    controller = CartController(service)
    try:
        user_id: UUID = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await controller.add_new_item_to_cart(user_id, cart_item)
    except HTTPException as e:
        raise e


@router.delete("/delete")
async def delete_item_from_cart(cart_item: CartItemUpdate, current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = CartService(session)
    controller = CartController(service)
    try:
        user_id: UUID = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await controller.delete_item_from_cart(user_id, cart_item)
    except HTTPException as e:
        raise e
