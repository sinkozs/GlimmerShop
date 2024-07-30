from services.checkout_service import CheckoutService
from schemas.schemas import CartItemForCheckout
from typing import List
from fastapi import HTTPException, Depends


class CheckoutController:

    def __init__(self, service: CheckoutService):
        self._service = service

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        try:
            return await self._service.create_checkout_session(cart_items)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def update_stock_quantity(self, cart_items: List[CartItemForCheckout]):
        try:
            return await self._service.update_stock_quantity(cart_items)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
