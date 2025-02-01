from typing import List

from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from controllers.category_controller import CategoryController
from services.category_service import CategoryService
from dependencies import get_session, get_current_user
from schemas.schemas import (
    CategoryUpdate,
    CategoryQuery,
    CategoryToProductRequest,
    CategoryIdentifiers,
)

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"Category": "Not found"}},
)


def get_category_service(
    session: AsyncSession = Depends(get_session),
) -> CategoryService:
    return CategoryService(session)


def get_category_controller(
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryController:
    return CategoryController(category_service)


@router.get("")
async def get_all_categories(
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.get_all_categories()


@router.get("/{category_id}")
async def get_category_name_by_id(
    category_id: int, controller: CategoryController = Depends(get_category_controller)
):
    return await controller.get_category_name_by_id(category_id)


@router.get("/search/", response_model=List[CategoryQuery])
async def search_categories(
    query: str = Query(...),
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.search_categories(query)


@router.post("/category-by-identifier")
async def get_category_by_identifier(
    category_identifier: CategoryIdentifiers,
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.get_category_by_identifier(category_identifier)


@router.get("/product-categories/{product_id}")
async def get_product_categories(
    product_id: int, controller: CategoryController = Depends(get_category_controller)
) -> dict:
    return await controller.get_product_categories(product_id)


@router.get("/products-by-category/{category_id}")
async def get_products_by_category(
    category_id: int, controller: CategoryController = Depends(get_category_controller)
):
    return await controller.get_products_by_category(category_id)


@router.get("/categories/sellers/{category_id}/products")
async def get_seller_products_by_category(
    category_id: int,
    current_user: dict = Depends(get_current_user),
    controller: CategoryController = Depends(get_category_controller),
):
    seller_id: UUID = current_user.get("user_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Missing seller ID")
    return await controller.get_seller_products_by_category(category_id, seller_id)


@router.post("/new")
async def add_new_category(
    category_name: CategoryUpdate,
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.add_new_category(category_name)


@router.post("/add-category-to-product")
async def add_category_to_product(
    request: CategoryToProductRequest,
    controller: CategoryController = Depends(get_category_controller),
):
    print(request)
    return await controller.add_category_to_product(request)


@router.put("/edit")
async def edit_category(
    category_id: int,
    category_update: CategoryUpdate,
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.edit_category(category_id, category_update)


@router.delete("/delete-category-from-product")
async def delete_category_from_product(
    request: CategoryToProductRequest,
    controller: CategoryController = Depends(get_category_controller),
):
    return await controller.delete_category_from_product(
        request.product_id, request.category_id
    )
