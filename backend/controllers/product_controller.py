
from sqlalchemy.dialects.postgresql import UUID

from dependencies import dict_to_db_model, db_model_to_dict
from services.user_service import UserService
from services.product_service import ProductService
from services.user_service import UserService
from models.models import User, Product
from config.auth_config import bcrypt_context
from schemas.schemas import ProductCreate
from datetime import datetime, timezone
from exceptions.user_exceptions import UserException
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException


class ProductController:

    def __init__(self, service: ProductService):
        self._service = service

    async def get_product_by_id(self, product_id: int) -> dict:
        try:
            return await self._service.get_product_by_id(product_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_products(self):
        try:
            return await self._service.get_all_products()
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_products_by_seller(self, seller_id: UUID):
        try:
            return await self._service.get_all_products_by_seller(seller_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_product(self, seller_id: UUID, new_product: ProductCreate):
        product = Product()
        product.name = new_product.name
        product.description = new_product.description
        product.price = new_product.price
        product.color = new_product.color
        product.material = new_product.material
        product.stock_quantity = new_product.stock_quantity
        product.image_path = new_product.image_path
        product.image_path2 = new_product.image_path2
        product.seller_id = seller_id

        try:
            await self._service.add_new_product(seller_id, product)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_product(self, product_id: int):
        try:
            await self._service.delete_product(product_id)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e