from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from dependencies import get_session
from controllers.product_controller import ProductController
from services.product_service import ProductService
from schemas.schemas import ProductCreate, ProductUpdate, PriceFilter, MaterialsFilter
from dependencies import get_current_user

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
        resp = await product_controller.get_product_by_id(product_id)
        print(resp)
        return resp
    except HTTPException as e:
        raise e


@router.post("/filter_by_price")
async def get_products_by_price_range(category_id: int, price_range: PriceFilter,
                                      session: AsyncSession = Depends(get_session)):
    try:
        service = ProductService(session)
        product_controller = ProductController(service)
        return await product_controller.get_products_by_price_range(category_id, price_range)
    except HTTPException as e:
        raise e


@router.post("/filter_by_material")
async def get_products_by_material(category_id: int, materials: MaterialsFilter,
                                   session: AsyncSession = Depends(get_session)):
    try:
        service = ProductService(session)
        product_controller = ProductController(service)
        return await product_controller.get_products_by_material(category_id, materials)
    except HTTPException as e:
        raise e


@router.post("/filter_by_material_and_price")
async def filter_products_by_material_and_price(category_id: int, materials: MaterialsFilter, price_range: PriceFilter,
                                   session: AsyncSession = Depends(get_session)):
    try:
        service = ProductService(session)
        product_controller = ProductController(service)
        return await product_controller.filter_products_by_material_and_price(category_id, materials, price_range)
    except HTTPException as e:
        raise e


@router.post("/new")
async def add_new_product(product: ProductCreate, current_user: dict = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        seller_id: UUID = current_user.get("id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="Missing seller ID")
        return await product_controller.add_new_product(seller_id, product)
    except HTTPException as e:
        raise e


@router.post("/upload-image")
async def add_new_product(product_id: int, image_number: int, image: UploadFile = File(...),
                          session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        if image_number in (1, 2):
            return await product_controller.upload_image(product_id, image_number, image)
        else:
            raise HTTPException(status_code=400, detail="Image number can be only 1 or 2")
    except HTTPException as e:
        raise e


@router.put("/edit/{product_id}")
async def edit_product(product_id: int, product: ProductUpdate, current_user: dict = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        seller_id: UUID = current_user.get("id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="Missing seller ID")
        return await product_controller.edit_product(product_id, product)
    except HTTPException as e:
        raise e


@router.delete("/delete/{product_id}")
async def delete_product(product_id: int, current_user: dict = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    service = ProductService(session)
    product_controller = ProductController(service)
    try:
        seller_id: UUID = current_user.get("id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="Missing seller ID")

        print(f"Seller id: {seller_id}")
        return await product_controller.delete_product(product_id)
    except HTTPException as e:
        raise e
