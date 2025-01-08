from typing import List

from sqlalchemy.dialects.postgresql import UUID
from PIL import Image
from services.product_service import ProductService
from services.category_service import CategoryService
from models.models import Product
from schemas.schemas import (
    ProductUpdate,
    PriceFilter,
    MaterialsFilter,
    ProductData,
    ProductFilterRequest,
)
from exceptions.user_exceptions import UserException
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException, Query


class ProductController:

    def __init__(self, service: ProductService, category_service: CategoryService):
        self._service = service
        self._category_service = category_service

    async def get_product_by_id(self, product_id: int) -> dict:
        try:
            return await self._service.get_product_by_id(product_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_products(self) -> list:
        try:
            return await self._service.get_all_products()
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_products_by_seller(self, seller_id: UUID) -> list[dict]:
        try:
            return await self._service.get_all_products_by_seller(seller_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_products_by_price_range(
        self, category_id: int, price_range: PriceFilter
    ) -> list:
        try:
            return await self._service.get_products_by_price_range(
                category_id, price_range
            )
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_products_by_material(
        self, category_id: int, materials: MaterialsFilter
    ) -> list:
        try:
            return await self._service.get_products_by_material(category_id, materials)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def filter_products_by_material_price_and_seller(
        self, filters: ProductFilterRequest
    ):
        try:
            return await self._service.get_filtered_products(filters)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    async def search_products(
        self, query: str = Query(...), seller_id: UUID = Query(...)
    ) -> List[ProductData]:
        try:
            return await self._service.search_products(query, seller_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_product(
        self, seller_id: UUID, new_product: ProductData
    ) -> dict[str, int]:
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
            product_id = await self._service.add_new_product(seller_id, product)
            if new_product.categories:
                for category_id in new_product.categories:
                    await self._category_service.add_category_to_product(
                        product_id, category_id
                    )

            return {"product_id": product_id}
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def upload_image(self, product_id: int, image_number: int, image: Image):
        try:
            await self._service.upload_image(product_id, image_number, image)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_product(self, product_id: int, edited_product: ProductUpdate):
        try:
            await self._service.edit_product(product_id, edited_product)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_product(self, product_id: int):
        try:
            await self._service.delete_product(product_id)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
