from exceptions.order_exceptions import OrderException
from services.order_service import OrderService
from fastapi import HTTPException


class OrderController:

    def __init__(self, service: OrderService):
        self._service = service

    async def get_order_by_id(self, order_id: int) -> dict:
        try:
            user: dict = await self._service.get_order_by_id(order_id=order_id)
            return user
        except OrderException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
