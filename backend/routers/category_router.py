from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from controllers.product_controller import ProductController
from controllers.category_controller import CategoryController
from services.product_service import ProductService
from services.category_service import CategoryService
from dependencies import get_current_user, get_session
from schemas.schemas import CategoryUpdate


from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"Category": "Not found"}}
)


@router.get("")
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_all_categories()
    except HTTPException as e:
        raise e


@router.get("/category-by-identifier")
async def get_category_by_identifier(category_identifier, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_category_by_identifier(category_identifier)
    except HTTPException as e:
        raise e


@router.get("/product-categories")
async def get_product_categories(product_id: int, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_product_categories(product_id)
    except HTTPException as e:
        raise e


@router.get("/products-by-category")
async def get_products_by_category(category_id: int, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.get_products_by_category(category_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def add_new_category(category_name: str, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.add_new_category(category_name)
    except HTTPException as e:
        raise e


@router.post("/add-category-to-product")
async def add_category_to_product(product_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.add_category_to_product(product_id, category_id)
    except HTTPException as e:
        raise e


@router.put("/edit")
async def edit_category(category_id: int, category_update: CategoryUpdate, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.edit_category(category_id, category_update)
    except HTTPException as e:
        raise e


@router.delete("/delete-category-from-product")
async def delete_category_from_product(product_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    controller = CategoryController(service)
    try:
        return await controller.delete_category_from_product(product_id, category_id)
    except HTTPException as e:
        raise e