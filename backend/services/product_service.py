import os
from uuid import UUID
from typing import List
from PIL import Image
from io import BytesIO
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, UploadFile, File
from sqlalchemy import func, and_, exists, or_
from models.models import Product, Category, ProductCategory
from schemas.schemas import ProductUpdate, PriceFilter, MaterialsFilter, ProductData
from .user_service import UserService
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict, is_valid_update


class ProductService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_product_by_id(self, product_id: int) -> dict:
        try:
            stmt = select(Product).where(Product.id == product_id)
            result = await self.db.execute(stmt)
            product: Product = result.scalars().first()
            if product:
                return db_model_to_dict(product)
            else:
                raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                       detail=f"Product with id {product_id} not found!")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def product_exists(self, product_id: int) -> bool:
        stmt = select(exists().where(Product.id == product_id))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_all_products_by_seller(self, seller_id: UUID) -> list:
        try:
            user_service = UserService(self.db)
            if not await user_service.check_seller_exists(seller_id):
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No seller found with id {seller_id}"
                )

            stmt = select(Product).filter(Product.seller_id == seller_id)
            result = await self.db.execute(stmt)
            products = result.scalars().all()
            if products:
                product_data = [db_model_to_dict(q) for q in products]
                return product_data
            else:
                raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                       detail=f"Product with seller id {seller_id} not found!")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_all_categories_for_product(self, product_id: int) -> List[dict]:
        try:
            product_service = ProductService(self.db)
            if not await product_service.check_product_exists(product_id):
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No product found with id {product_id}"
                )

            stmt = select(Category).filter(Category)
            result = await self.db.execute(stmt)
            categories = result.scalars().all()
            if categories:
                product_data = [db_model_to_dict(c) for c in categories]
                return product_data
            else:
                raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                       detail=f"Categories with product id {product_id} not found!")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_all_products(self) -> List[dict]:
        try:
            async with self.db.begin():
                result = await self.db.execute(select(Product))
                products = result.scalars().all()
                if products:
                    product_data = [db_model_to_dict(product) for product in products]
                    return product_data
                else:
                    raise ProductException()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_products_by_price_range(self, category_id: int, price_range: PriceFilter) -> list:
        try:
            async with self.db.begin():
                stmt = (
                    select(Product)
                    .join(Product.product_category)
                    .filter(ProductCategory.category_id == category_id)
                    .filter((Product.price >= price_range.min_price) & (Product.price <= price_range.max_price))
                )

                result = await self.db.execute(stmt)
                products = result.scalars().all()
                if products:
                    product_data = [db_model_to_dict(q) for q in products]
                    return product_data
                else:
                    raise ProductException(detail="Failed to fetch products by price range")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_products_by_material(self, category_id: int, materials: MaterialsFilter) -> list:
        try:
            async with self.db.begin():
                material_conditions = [Product.material.ilike(f"%{material}%") for material in materials.materials]
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
                    raise ProductException(detail="Failed to fetch products by material")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def check_product_exists(self, product_id: int) -> bool:
        try:
            async with self.db.begin():
                stmt = select(func.count()).where(and_(
                    Product.id == product_id,
                ))
                result = await self.db.execute(stmt)
                return result.scalar_one() > 0
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise

    async def search_products(self, query: str, seller_id: UUID) -> List[ProductData]:
        async with self.db.begin():
            try:
                query_as_uuid = UUID(query)
            except ValueError:
                query_as_uuid = None

            stmt = select(Product).where(
                (Product.seller_id == seller_id) &
                (
                        Product.name.ilike(f"%{query}%") |
                        (Product.id == query_as_uuid if query_as_uuid else False)
                )
            )
            result = await self.db.execute(stmt)
            products = result.scalars().all()
            return [ProductData.model_validate(product) for product in products]

    async def add_new_product(self, seller_id: UUID, product: Product):
        try:
            user_service = UserService(self.db)
            if not await user_service.check_seller_exists(seller_id):
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No seller found with id {seller_id}"
                )
            self.db.add(product)
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def upload_image(self, product_id: int, image_number: int, image: UploadFile = File(...)):
        try:
            image_data = await image.read()
            original_image = Image.open(BytesIO(image_data))

            # Resize the image
            max_size = (564, 564)
            original_image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert RGBA to RGB if necessary
            if original_image.mode == 'RGBA':
                original_image = original_image.convert('RGB')

            output_buffer = BytesIO()
            original_image.save(output_buffer, format="JPEG")
            output_buffer.seek(0)

            filename = image.filename
            # Ensure the filename has a valid extension
            if not filename.lower().endswith(('.jpg', '.jpeg', '.jfif', '.png')):
                filename += ".jpg"

            save_path = os.path.join(os.path.dirname(__file__), '..', 'images', filename)
            full_path = os.path.abspath(save_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "wb") as f:
                f.write(output_buffer.getvalue())

            original_image.close()
            output_buffer.close()

            # Update the product with the image path
            edited_product = ProductUpdate()
            print(f"Image filename: {filename}")
            if image_number == 1:
                edited_product.image_path = f"images/{filename}"
            elif image_number == 2:
                edited_product.image_path2 = f"images/{filename}"
            if await self.edit_product(product_id, edited_product):
                return {"message": "Image uploaded and resized successfully"}
        except Exception as e:
            return {"error": str(e)}

    async def edit_product(self, product_id: int, edited_product: ProductUpdate):
        async with self.db.begin():
            stmt = select(Product).where(Product.id == product_id)
            result = await self.db.execute(stmt)
            product: Product = result.scalars().first()

            if product is None:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No product found with id {product_id}"
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
            await self.db.commit()

    async def delete_product(self, product_id: int):
        try:
            async with self.db.begin():
                stmt = select(Product).filter(Product.id == product_id)
                product: Product = await self.db.scalar(stmt)

            if product is not None:
                await self.db.delete(product)

        except NoResultFound:
            raise UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with {product_id} id not found!"
            )
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")
