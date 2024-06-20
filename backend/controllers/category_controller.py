
from sqlalchemy.dialects.postgresql import UUID

from dependencies import dict_to_db_model, db_model_to_dict
from services.user_service import UserService
from services.product_service import ProductService
from services.user_service import UserService
from services.category_service import CategoryService
from models.models import User, Product, Category
from config.auth_config import bcrypt_context
from schemas.schemas import ProductCreate
from datetime import datetime, timezone
from exceptions.user_exceptions import UserException
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException


class CategoryController:

    def __init__(self, service: CategoryService):
        self._service = service

    async def get_category_by_identifier(self, category_identifier) -> dict:
        try:
            category_exists = await self._service.check_category_exists(category_identifier)
            return category_exists
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_categories(self):
        try:
            return await self._service.get_all_categories()
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_product_categories(self, product_id: int):
        try:
            return await self._service.get_product_categories(product_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_products_by_category(self, category_id: int):
        try:
            return await self._service.get_products_by_category(category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_category(self, category_name: str):
        try:
            category_exists = await self._service.check_category_exists(category_name)
            if not category_exists.get("is_exist"):
                category = Category()
                category.category_name = category_name
                await self._service.add_new_category(category)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_category_to_product(self, product_id: int, category_id: int):
        try:
            category_exists = await self._service.check_category_exists(category_id)
            if category_exists.get("is_exist"):
                await self._service.add_category_to_product(product_id, category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
            await self._service.delete_category_from_product(product_id, category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e