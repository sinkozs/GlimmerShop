from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session
from controllers.user_controller import UserController
from services.user_service import UserService
from controllers.product_controller import ProductController
from services.product_service import ProductService
from schemas.schemas import ProductCreate

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"Product": "Not found"}}
)


@router.get("")
async def get_all_products(session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        return await product_controller.get_all_products()
    except HTTPException as e:
        raise e


@router.get("/products-by-seller")
async def get_products_by_seller(seller_id: UUID, session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        return await product_controller.get_all_products_by_seller(seller_id)
    except HTTPException as e:
        raise e


@router.get("/{product_id}")
async def get_product_by_id(product_id: int,
                         session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        return await product_controller.get_product_by_id(product_id)
    except HTTPException as e:
        raise e


@router.post("/new")
async def add_new_product(seller_id: UUID, product: ProductCreate, session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        return await product_controller.add_new_product(seller_id, product)
    except HTTPException as e:
        raise e
