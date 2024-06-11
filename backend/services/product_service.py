from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import Product, User
from .user_service import UserService
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict


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
