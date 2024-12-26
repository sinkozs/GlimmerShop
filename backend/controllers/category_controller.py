from typing import List

from services.category_service import CategoryService
from schemas.schemas import CategoryUpdate, CategoryQuery
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException, Query, status


class CategoryController:

    def __init__(self, service: CategoryService):
        self._service = service

    async def get_category_by_identifier(self, category_identifier) -> dict:
        try:
            category_exists = await self._service.check_category_exists(
                category_identifier
            )
            return category_exists
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_categories(self):
        try:
            return await self._service.get_all_categories()
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_product_categories(self, product_id: int) -> list:
        try:
            return await self._service.get_product_categories(product_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def search_categories(self, query: str = Query(...)) -> List[CategoryQuery]:
        try:
            return await self._service.search_categories(query)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_products_by_category(self, category_id: int):
        try:
            return await self._service.get_products_by_category(category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_category(self, category: CategoryUpdate) -> int:
        try:
            category_name = category.category_name
            category_exists = await self._service.check_category_exists(category_name)
            if not category_exists.get("is_exist"):
                return await self._service.add_new_category(category_name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{category_name}' already exists",
            )
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_category(self, category_id: int, category_update: CategoryUpdate):
        try:
            category_exists = await self._service.check_category_exists(category_id)
            if category_exists.get("is_exist"):
                await self._service.edit_category(category_id, category_update)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_category_to_product(self, product_id: int, category_id: int):
        try:
            category_exists = await self._service.check_category_exists(category_id)
            if category_exists.get("is_exist"):
                return await self._service.add_category_to_product(
                    product_id, category_id
                )

        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
            await self._service.delete_category_from_product(product_id, category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
