from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from sqlalchemy.future import select
from schemas.schemas import CartItemForCheckout
from config.parser import load_config
from models.models import Product
from exceptions.product_exceptions import ProductException
from services.checkout_service import CheckoutService
from controllers.checkout_controller import CheckoutController
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import stripe

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    responses={500: {"Checkout": "Error when creating checkout session"}}
)


@router.post("/create-checkout-session")
async def create_checkout_session(cart_items: List[CartItemForCheckout], session: AsyncSession = Depends(get_session)):
    service = CheckoutService(session)
    controller = CheckoutController(service)
    try:
        return await controller.create_checkout_session(cart_items)
    except HTTPException as e:
        raise e


@router.put("/update-stock")
async def update_stock(cart_items: List[CartItemForCheckout], session: AsyncSession = Depends(get_session)):
    service = CheckoutService(session)
    controller = CheckoutController(service)
    try:
        return await controller.update_stock_quantity(cart_items)
    except HTTPException as e:
        raise e
