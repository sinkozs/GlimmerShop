from typing import List

from services.category_service import CategoryService
from schemas.schemas import (
    CategoryUpdate,
    CategoryQuery,
    CategoryToProductRequest,
    CategoryIdentifiers,
)
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException, Query, status


class CategoryController:

    def __init__(self, service: CategoryService):
        self._service = service

    async def get_category_by_identifier(
        self, category_identifier: CategoryIdentifiers
    ) -> dict:
        try:
            if category_identifier.category_id:
                category = await self._service.get_category_by_id(
                    category_identifier.category_id
                )
            elif category_identifier.category_name:
                category = await self._service.get_category_by_name(
                    category_identifier.category_name
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category ID or name must be provided",
                )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )
            return category
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_categories(self):
        try:
            return await self._service.get_all_categories()
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_category_name_by_id(self, category_id: int) -> dict:
        try:
            return await self._service.get_category_by_id(category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_product_categories(self, product_id: int) -> dict:
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
            category = await self._service.get_category_by_name(category_name)
            if not category:
                return await self._service.add_new_category(category_name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{category_name}' already exists",
            )
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_category(self, category_id: int, category_update: CategoryUpdate):
        try:
            category_exists = await self._service.get_category_by_id(category_id)
            if category_exists.get("is_exist"):
                await self._service.edit_category(category_id, category_update)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_category_to_product(self, request: CategoryToProductRequest):
        try:
            category = await self._service.get_category_by_id(request.category_id)
            if category:
                return await self._service.add_category_to_product(
                    request.product_id, request.category_id
                )

        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
            await self._service.delete_category_from_product(product_id, category_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
