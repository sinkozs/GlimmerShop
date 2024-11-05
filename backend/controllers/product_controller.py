from typing import List

from sqlalchemy.dialects.postgresql import UUID
from PIL import Image
from services.product_service import ProductService
from models.models import Product
from schemas.schemas import ProductCreate, ProductUpdate, PriceFilter, MaterialsFilter, ProductData, SellerFilter, \
    ProductFilterRequest
from exceptions.user_exceptions import UserException
from exceptions.product_exceptions import ProductException
from fastapi import HTTPException, Query


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

    async def get_products_by_price_range(self, category_id: int, price_range: PriceFilter) -> set:
        try:
            return await self._service.get_products_by_price_range(category_id, price_range)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_products_by_material(self, category_id: int, materials: MaterialsFilter) -> set:
        try:
            return await self._service.get_products_by_material(category_id, materials)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e


    def get_common_products(self, products_by_material, products_by_price_range, products_by_seller):
        material_ids = {product['id'] for product in products_by_material}
        price_range_ids = {product['id'] for product in products_by_price_range}
        seller_ids = {product['id'] for product in products_by_seller}

        common_ids = material_ids

        if price_range_ids:
            common_ids = common_ids & price_range_ids

        if seller_ids:
            common_ids = common_ids & seller_ids

        all_products = {product['id']: product for product in
                        products_by_material + products_by_price_range + products_by_seller}

        common_products = [all_products[product_id] for product_id in common_ids]
        return common_products

    async def filter_products_by_material_price_and_seller(self, filters: ProductFilterRequest):
        try:
            products_by_material, products_by_price_range, products_by_seller = list(), list(), list()
            if filters.materials:
                products_by_material = await self._service.get_products_by_material(filters.category_id,
                                                                                    filters.materials)
            products_by_price_range = await self._service.get_products_by_price_range(filters.category_id,
                                                                                      filters.price_range)
            if filters.seller.seller_id:
                products_by_seller = await self._service.get_all_products_by_seller(filters.seller.seller_id)
            return self.get_common_products(products_by_material, products_by_price_range, products_by_seller)

        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def search_products(self, query: str = Query(...), seller_id: UUID = Query(...)) -> List[ProductData]:
        try:
            return await self._service.search_products(query, seller_id)
        except ProductException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def add_new_product(self, seller_id: UUID, new_product: ProductCreate) -> int:
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
            return await self._service.add_new_product(seller_id, product)
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
