
from sqlalchemy.dialects.postgresql import UUID

from dependencies import dict_to_db_model, db_model_to_dict
from services.cart_service import CartService
from schemas.schemas import CartItemCreate
from models.models import User, Product, Cart, CartItem
from exceptions.cart_exceptions import CartException
from fastapi import HTTPException


class CartController:

    def __init__(self, service: CartService):
        self._service = service

    async def add_new_item_to_cart(self, user_id: UUID, new_cart_item: CartItemCreate):
        try:
            await self._service.add_new_item_to_cart(user_id, new_cart_item)
        except CartException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

