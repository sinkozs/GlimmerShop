from typing import List
from fastapi import APIRouter, Depends
from dependencies import get_session
from services.order_service import OrderService
from controllers.order_controller import OrderController
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/order",
    tags=["order"],
    responses={500: {"Order": "Error with the order"}},
)


def get_order_service(
    session: AsyncSession = Depends(get_session),
) -> OrderService:
    return OrderService(session)


def get_order_controller(
    order_service: OrderService = Depends(get_order_service),
) -> OrderController:
    return OrderController(order_service)