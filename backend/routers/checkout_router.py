from typing import List
from fastapi import APIRouter, Depends
from dependencies import get_session
from schemas.schemas import CartItemForCheckout, GuestUserInfo, OrderData
from services.checkout_service import CheckoutService
from services.order_service import OrderService
from controllers.checkout_controller import CheckoutController
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    responses={500: {"Checkout": "Error when creating checkout session"}},
)


def get_checkout_service(
        session: AsyncSession = Depends(get_session),
) -> CheckoutService:
    return CheckoutService(session)


def get_order_service(
        session: AsyncSession = Depends(get_session),
) -> OrderService:
    return OrderService(session)


def get_checkout_controller(
        checkout_service: CheckoutService = Depends(get_checkout_service),
        order_service: OrderService = Depends(get_order_service)) -> CheckoutController:
    return CheckoutController(checkout_service, order_service)


@router.post("/create-checkout-session")
async def create_checkout_session(
        cart_items: List[CartItemForCheckout],
        controller: CheckoutController = Depends(get_checkout_controller),
):
    return await controller.create_checkout_session(cart_items)


@router.post("/post-checkout")
async def post_checkout_updates(
        orders: List[OrderData],
        guest_user_info: GuestUserInfo,
        controller: CheckoutController = Depends(get_checkout_controller),
):
    return await controller.post_checkout_updates(orders, guest_user_info)
