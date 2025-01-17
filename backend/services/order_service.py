from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status

from config.logger_config import get_logger
from dependencies import db_model_to_dict, generate_random_12_digit_number
from exceptions.order_exceptions import OrderException
from exceptions.user_exceptions import UserException
from models.models import User, Order, OrderItem
from sqlalchemy.orm import joinedload

from schemas.schemas import OrderData, GuestUserInfo
from services.user_service import UserService


class OrderService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.logger = get_logger(__name__)

    async def get_order_by_id(self, order_id: int) -> dict:
        try:
            stmt = (
                select(Order)
                .options(joinedload(Order.items))
                .where(Order.id == order_id)
            )
            result = await self.db.execute(stmt)
            order: Order = result.unique().scalars().first()

            if order:
                order_dict = db_model_to_dict(order)
                order_dict["items"] = [db_model_to_dict(item) for item in order.items]
                return order_dict
            else:
                raise OrderException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order with id {order_id} not found!",
                )
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_order_by_id: {e}")
            raise OrderException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def add_new_order(
            self,
            orders: List[OrderData],
            guest_user_info: GuestUserInfo) -> int:
        try:
            current_time = datetime.now()
            tracking_number = generate_random_12_digit_number()

            new_order = Order(
                user_id=guest_user_info.user_id if guest_user_info.user_id else None,
                first_name=guest_user_info.first_name,
                last_name=guest_user_info.last_name,
                email=guest_user_info.email,
                shipping_address=guest_user_info.shipping_address,
                phone=guest_user_info.phone,
                status="confirmed",
                created_at=current_time,
                tracking_number=tracking_number
            )
            self.db.add(new_order)
            await self.db.flush()

            order_items = [
                OrderItem(
                    order_id=new_order.id,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    price_at_purchase=order.price
                )
                for order in orders
            ]
            self.db.add_all(order_items)
            await self.db.flush()

            return new_order.id

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in add_new_order: {e}")
            raise OrderException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!"
            )
