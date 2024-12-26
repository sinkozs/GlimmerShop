from typing import List
from fastapi import APIRouter, Depends
from dependencies import get_session
from schemas.schemas import CartItemForCheckout
from services.checkout_service import CheckoutService
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


def get_checkout_controller(
    checkout_service: CheckoutService = Depends(get_checkout_service),
) -> CheckoutController:
    return CheckoutController(checkout_service)


@router.post("/create-checkout-session")
async def create_checkout_session(
    cart_items: List[CartItemForCheckout],
    controller: CheckoutController = Depends(get_checkout_controller),
):
    return await controller.create_checkout_session(cart_items)


@router.put("/update-stock")
async def update_stock(
    cart_items: List[CartItemForCheckout],
    controller: CheckoutController = Depends(get_checkout_controller),
):
    return await controller.update_stock_quantity(cart_items)
