import os
from uuid import UUID
from typing import List
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, UploadFile, File, HTTPException
from sqlalchemy import func, and_, exists, or_

from config.logger_config import get_logger
from models.models import Product, Category, ProductCategory
from schemas.schemas import (
    ProductUpdate,
    PriceFilter,
    MaterialsFilter,
    SellerFilter,
    ProductData,
    ProductFilterRequest,
)
from .user_service import UserService
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict, is_valid_update


class ProductService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.logger = get_logger(__name__)

    async def get_product_by_id(self, product_id: int) -> dict:
        try:
            stmt = select(Product).where(Product.id == product_id)
            result = await self.db.execute(stmt)
            product: Product = result.scalars().first()
            if product:
                return db_model_to_dict(product)
            else:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {product_id} not found!",
                )
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_product_by_id: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def product_exists(self, product_id: int) -> bool:
        try:
            stmt = select(exists().where(Product.id == product_id))
            result = await self.db.execute(stmt)
            return result.scalar()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in product_exists: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_all_products_by_seller(self, seller_id: UUID) -> list:
        user_service = UserService(self.db)
        if not await user_service.check_seller_exists(seller_id):
            raise UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No seller found with id {seller_id}",
            )

        stmt = select(Product).filter(Product.seller_id == seller_id)
        result = await self.db.execute(stmt)
        products = result.scalars().all()
        if products:
            return [db_model_to_dict(product) for product in products]
        else:
            return []

    async def get_all_categories_for_product(self, product_id: int) -> List[dict]:
        try:
            product_service = ProductService(self.db)
            if not await product_service.check_product_exists(product_id):
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No product found with id {product_id}",
                )

            stmt = select(Category).filter(Category)
            result = await self.db.execute(stmt)
            categories = result.scalars().all()
            if categories:
                product_data = [db_model_to_dict(c) for c in categories]
                return product_data
            else:
                return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_all_categories_for_product: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_all_products(self) -> List[dict]:
        try:
            result = await self.db.execute(select(Product))
            products = result.scalars().all()
            if products:
                product_data = [db_model_to_dict(product) for product in products]
                return product_data
            else:
                return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_all_products: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def filter_by_price_range(
            self, category_id: int, price_range: PriceFilter
    ) -> list:
        try:
            stmt = (
                select(Product)
                .join(Product.product_category)
                .filter(ProductCategory.category_id == category_id)
                .filter(
                    (Product.price >= price_range.min_price)
                    & (Product.price <= price_range.max_price)
                )
            )

            result = await self.db.execute(stmt)
            products = result.scalars().all()
            if products:
                product_data = [db_model_to_dict(q) for q in products]
                return product_data
            else:
                return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_products_by_price_range: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def filter_by_material(
            self, category_id: int, materials: MaterialsFilter
    ) -> list:
        try:
            extended_materials = set()
            for material in materials.materials:
                words = material.lower().split()
                extended_materials.update(words)
            material_conditions = [
                Product.material.ilike(f"%{word}%") for word in extended_materials
            ]

            stmt = (
                select(Product)
                .join(Product.product_category)
                .filter(ProductCategory.category_id == category_id)
                .filter(or_(*material_conditions))
            )

            result = await self.db.execute(stmt)
            products = result.scalars().all()
            if products:
                product_data = [db_model_to_dict(p) for p in products]
                return product_data
            else:
                return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_products_by_material: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def filter_by_seller(
            self, category_id: int, seller_id: UUID
    ) -> list:
        try:
            stmt = (
                select(Product)
                .join(Product.product_category)
                .filter(ProductCategory.category_id == category_id)
                .filter(Product.seller_id == seller_id)
            )

            result = await self.db.execute(stmt)
            products = result.scalars().all()
            if products:
                product_data = [db_model_to_dict(p) for p in products]
                return product_data
            else:
                return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_products_by_seller: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_filtered_products(self, filters: ProductFilterRequest) -> list:
        try:
            stmt = (
                select(Product)
                .join(Product.product_category)
                .filter(ProductCategory.category_id == filters.category_id)
            )

            if filters.materials:
                material_conditions = [
                    Product.material.ilike(f"%{word}%")
                    for material in filters.materials.materials
                    for word in material.lower().split()
                ]
                stmt = stmt.filter(or_(*material_conditions))
            if filters.price_range:
                stmt = stmt.filter(
                    Product.price.between(
                        filters.price_range.min_price, filters.price_range.max_price
                    )
                )
            if filters.seller.seller_id:
                stmt = stmt.filter(Product.seller_id == filters.seller.seller_id)

            result = await self.db.execute(stmt)
            products = result.scalars().all()
            return [db_model_to_dict(p) for p in products] if products else []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_products_by_material: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    def get_common_products(
            self, products_by_material, products_by_price_range, products_by_seller
    ):
        id_sets = []

        if products_by_material:
            id_sets.append({p["id"] for p in products_by_material})
        if products_by_price_range:
            id_sets.append({p["id"] for p in products_by_price_range})
        if products_by_seller:
            id_sets.append({p["id"] for p in products_by_seller})

        common_ids = set.intersection(*id_sets) if id_sets else set()

        all_products = {
            p["id"]: p
            for p in products_by_material + products_by_price_range + products_by_seller
        }
        return [all_products[pid] for pid in common_ids]

    async def check_product_exists(self, product_id: int) -> bool:
        try:
            stmt = select(func.count()).where(
                and_(
                    Product.id == product_id,
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one() > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in check_product_exists: {e}")
            raise

    async def search_products(self, query: str, seller_id: UUID) -> List[ProductData]:
        try:
            query_as_uuid = UUID(query)
        except ValueError:
            query_as_uuid = None
        try:
            stmt = select(Product).where(
                (Product.seller_id == seller_id)
                & (
                        Product.name.ilike(f"%{query}%")
                        | (Product.id == query_as_uuid if query_as_uuid else False)
                )
            )
            result = await self.db.execute(stmt)
            products = result.scalars().all()
            return [ProductData.model_validate(product) for product in products]
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in search_products: {e}")
            raise

    async def add_new_product(self, seller_id: UUID, product: Product) -> int:
        try:
            user_service = UserService(self.db)
            if not await user_service.check_seller_exists(seller_id):
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No seller found with id {seller_id}",
                )
            self.db.add(product)
            await self.db.commit()
            await self.db.refresh(instance=product, attribute_names=["id"])
            return product.id
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in add_new_product: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def upload_image(
            self, product_id: int, image_number: int, image: UploadFile = File(...)
    ):
        try:
            product = await self.get_product_by_id(product_id)
            if not product:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found",
                )

            if image_number not in [1, 2]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image number must be 1 or 2",
                )

            if not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="File must be an image",
                )

            try:
                image_data = await image.read()
                original_image = Image.open(BytesIO(image_data))
            except UnidentifiedImageError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format",
                )

            try:
                # Resize the image
                max_size = (564, 564)
                original_image.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Convert RGBA to RGB if necessary
                if original_image.mode == "RGBA":
                    original_image = original_image.convert("RGB")

                output_buffer = BytesIO()
                original_image.save(output_buffer, format="JPEG")
                output_buffer.seek(0)

                filename = image.filename
                if not filename.lower().endswith((".jpg", ".jpeg", ".jfif", ".png")):
                    filename += ".jpg"

                save_path = os.path.join(
                    os.path.dirname(__file__), "..", "images", filename
                )
                full_path = os.path.abspath(save_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                try:
                    with open(full_path, "wb") as f:
                        f.write(output_buffer.getvalue())
                except IOError as e:
                    self.logger.error(f"Failed to save image: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to save image to filesystem",
                    )

                original_image.close()
                output_buffer.close()

                edited_product = ProductUpdate()
                if image_number == 1:
                    edited_product.image_path = f"images/{filename}"
                else:  # image_number == 2
                    edited_product.image_path2 = f"images/{filename}"

                try:
                    await self.edit_product(product_id, edited_product)
                except Exception as e:
                    self.logger.error(f"Failed to update product: {str(e)}")
                    if os.path.exists(full_path):
                        os.remove(full_path)
                    raise ProductException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update product with new image",
                    )

                return {
                    "status_code": status.HTTP_200_OK,
                    "detail": "Image uploaded and resized successfully",
                    "path": f"images/{filename}",
                }

            except Exception as e:
                self.logger.error(f"Error processing image: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to process image",
                )

        except (ProductException, HTTPException):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during image upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing the image",
            )

    async def edit_product(self, product_id: int, edited_product: ProductUpdate):
        try:
            stmt = select(Product).where(Product.id == product_id)
            result = await self.db.execute(stmt)
            product: Product = result.scalars().first()

            if product is None:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No product found with id {product_id}",
                )
            if is_valid_update(edited_product.name, product.name):
                product.name = edited_product.name
            if is_valid_update(edited_product.description, product.description):
                product.description = edited_product.description
            if is_valid_update(edited_product.price, product.price):
                product.price = edited_product.price
            if is_valid_update(edited_product.stock_quantity, product.stock_quantity):
                product.stock_quantity = edited_product.stock_quantity
            if is_valid_update(edited_product.material, product.material):
                product.material = edited_product.material
            if is_valid_update(edited_product.color, product.color):
                product.color = edited_product.color
            if is_valid_update(edited_product.image_path, product.image_path):
                product.image_path = edited_product.image_path
            if is_valid_update(edited_product.image_path2, product.image_path2):
                product.image_path2 = edited_product.image_path2

            self.db.add(product)
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in edit_product: {e}")
            raise

    async def delete_product(self, product_id: int):
        try:
            stmt = select(Product).filter(Product.id == product_id)
            product: Product = await self.db.scalar(stmt)

            if product is not None:
                await self.db.delete(product)

        except NoResultFound:
            raise ProductException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with {product_id} id not found!",
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in delete_product: {e}")
            raise ProductException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )
