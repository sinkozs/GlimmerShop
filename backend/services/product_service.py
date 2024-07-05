from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from sqlalchemy import func, and_, exists
from models.models import Product, User, ProductCategory, Category
from schemas.schemas import ProductCreate, ProductUpdate
from .user_service import UserService
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import dict_to_db_model, db_model_to_dict, is_valid_update


class ProductService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_product_by_id(self, product_id: int) -> dict:
        try:
            async with self.db.begin():
                stmt = select(Product).filter(Product.id == product_id)
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
            print(f"Product: {db_model_to_dict(product)}")
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
