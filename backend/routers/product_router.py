from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from dependencies import get_session
from controllers.product_controller import ProductController
from services.product_service import ProductService
from services.category_service import CategoryService
from schemas.schemas import (
    ProductUpdate,
    PriceFilter,
    MaterialsFilter,
    SellerFilter,
    ProductData,
    ProductFilterRequest,
)
from dependencies import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/products", tags=["products"], responses={404: {"Product": "Not found"}}
)


def get_product_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    return ProductService(session)


def get_category_service(
        session: AsyncSession = Depends(get_session),
) -> CategoryService:
    return CategoryService(session)


def get_product_controller(
        product_service: ProductService = Depends(get_product_service),
        category_service: CategoryService = Depends(get_category_service),
) -> ProductController:
    return ProductController(product_service, category_service)


@router.get("")
async def get_all_products(
        product_controller: ProductController = Depends(get_product_controller),
) -> list:
    return await product_controller.get_all_products()


@router.get("/products-by-seller")
async def get_products_by_seller(
        seller_id: UUID,
        product_controller: ProductController = Depends(get_product_controller),
) -> list:
    return await product_controller.get_all_products_by_seller(seller_id)


@router.get("/seller-dashboard")
async def get_seller_products_dashboard(
        seller_id: UUID,
        current_user: dict = Depends(get_current_user),
        product_controller: ProductController = Depends(get_product_controller),
) -> list:
    if UUID(current_user["user_id"]) != seller_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this seller dashboard"
        )
    return await product_controller.get_all_products_by_seller(seller_id)


@router.get("/{product_id}")
async def get_product_by_id(
        product_id: int,
        product_controller: ProductController = Depends(get_product_controller),
) -> dict:
    return await product_controller.get_product_by_id(product_id)


@router.get("/search/", response_model=List[ProductData])
async def search_products(
        query: str = Query(...),
        seller_id: UUID = Query(...),
        product_controller: ProductController = Depends(get_product_controller),
):
    return await product_controller.search_products(query, seller_id)


@router.post("/filter-by-price")
async def filter_by_price_range(
        category_id: int,
        price_range: PriceFilter,
        product_controller: ProductController = Depends(get_product_controller),
):
    return await product_controller.filter_by_price_range(
        category_id, price_range
    )


@router.post("/filter-by-material")
async def filter_by_material(
        category_id: int,
        materials: MaterialsFilter,
        product_controller: ProductController = Depends(get_product_controller),
):
    return await product_controller.filter_by_material(category_id, materials)


@router.post("/filter-by-seller")
async def filter_by_seller(
        category_id: int,
        seller_id: UUID,
        product_controller: ProductController = Depends(get_product_controller),
):
    return await product_controller.filter_by_seller(category_id, seller_id)


@router.post("/filter-by-material-price-and-seller")
async def filter_products_by_material_and_price(
        filters: ProductFilterRequest,
        product_controller: ProductController = Depends(get_product_controller),
):
    return await product_controller.filter_products_by_material_price_and_seller(
        filters
    )


@router.post("/new")
async def add_new_product(
        product: ProductData,
        current_user: dict = Depends(get_current_user),
        product_controller: ProductController = Depends(get_product_controller),
) -> dict:
    seller_id: UUID = current_user.get("user_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Missing seller ID")
    return await product_controller.add_new_product(seller_id, product)


@router.post("/upload-image")
async def upload_image(
        product_id: int,
        image_number: int,
        image: UploadFile = File(...),
        product_controller: ProductController = Depends(get_product_controller),
):
    if image_number in (1, 2):
        return await product_controller.upload_image(product_id, image_number, image)
    else:
        raise HTTPException(status_code=400, detail="Image number can be only 1 or 2")


@router.put("/edit")
async def edit_product(
        product_id: int,
        product: ProductUpdate,
        current_user: dict = Depends(get_current_user),
        product_controller: ProductController = Depends(get_product_controller),
):
    seller_id: UUID = current_user.get("user_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Missing seller ID")
    return await product_controller.edit_product(product_id, product)


@router.delete("/delete/{product_id}")
async def delete_product(
        product_id: int,
        current_user: dict = Depends(get_current_user),
        product_controller: ProductController = Depends(get_product_controller),
):
    seller_id: UUID = current_user.get("user_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Missing seller ID")

    return await product_controller.delete_product(product_id)
