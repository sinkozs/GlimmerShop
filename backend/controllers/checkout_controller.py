from services.checkout_service import CheckoutService
from services.order_service import OrderService
from schemas.schemas import CartItemForCheckout, GuestUserInfo, OrderData
from typing import List
from fastapi import HTTPException


class CheckoutController:

    def __init__(self, service: CheckoutService, order_service: OrderService):
        self._service = service
        self._order_service = order_service

    async def create_checkout_session(self, cart_items: List[CartItemForCheckout]):
        try:
            r =  await self._service.create_checkout_session(cart_items)
            print(r)
            return r
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def post_checkout_updates(self, order_data: List[OrderData], guest_user_info: GuestUserInfo):
        try:
            await self._service.update_stock_quantity(order_data)
            return await self._order_service.add_new_order(order_data, guest_user_info)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

