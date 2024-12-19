from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from controllers.category_controller import CategoryController
from services.category_service import CategoryService
from dependencies import get_session
from schemas.schemas import CategoryUpdate, CategoryQuery, CategoryToProductRequest

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"Category": "Not found"}},
)


@router.get("")
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        r = await controller.get_all_categories()
        print(r)
        return r
    except HTTPException as e:
        raise e


@router.get("/search/", response_model=List[CategoryQuery])
async def search_products(
    query: str = Query(...), session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.search_categories(query)
    except HTTPException as e:
        raise e


@router.get("/category-by-identifier")
async def get_category_by_identifier(
    category_identifier, session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_category_by_identifier(category_identifier)
    except HTTPException as e:
        raise e


@router.get("/product-categories")
async def get_product_categories(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> list:
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_product_categories(product_id)
    except HTTPException as e:
        raise e


@router.get("/products-by-category")
async def get_products_by_category(
    category_id: int, session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_products_by_category(category_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def add_new_category(
    category_name: str, session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.add_new_category(category_name)
    except HTTPException as e:
        raise e


@router.post("/add-category-to-product")
async def add_category_to_product(
    request: CategoryToProductRequest, session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.add_category_to_product(
            request.product_id, request.category_id
        )
    except HTTPException as e:
        raise e


@router.put("/edit")
async def edit_category(
    category_id: int,
    category_update: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.edit_category(category_id, category_update)
    except HTTPException as e:
        raise e


@router.delete("/delete-category-from-product")
async def delete_category_from_product(
    request: CategoryToProductRequest, session: AsyncSession = Depends(get_session)
):
    service = CategoryService(session)
    controller = CategoryController(service)
    print(request)
    try:
        return await controller.delete_category_from_product(
            request.product_id, request.category_id
        )
    except HTTPException as e:
        raise e
