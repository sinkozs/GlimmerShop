from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from sqlalchemy import func, and_
from models.models import Product, User, Category, ProductCategory
from .product_service import ProductService
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict, dict_to_db_model, convert_str_to_int_if_numeric


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all_categories(self) -> List[dict]:
        try:
            async with self.db.begin():
                result = await self.db.execute(select(Category))
                categories = result.scalars().all()
                if categories:
                    return [db_model_to_dict(c) for c in categories]
                else:
                    raise ProductException.category_not_found()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise ProductException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def check_category_exists(self, category_identifier: str) -> dict:
        try:
            category_identifier = convert_str_to_int_if_numeric(category_identifier)
            async with self.db.begin():
                # the identifier is the id
                if isinstance(category_identifier, int):
                    print(f"INT category_identifier: {category_identifier}")
                    condition = (Category.id == category_identifier)
                    # the identifier is the category name
                elif isinstance(category_identifier, str):
                    print(f"STR category_identifier: {category_identifier}")
                    condition = (Category.category_name == category_identifier)
                else:
                    raise ValueError("Invalid category identifier type")

                stmt = select(Category).where(condition)
                result = await self.db.execute(stmt)
                category_record = result.scalar_one_or_none()
                if category_record:
                    return {"is_exist": True, "category_record": db_model_to_dict(category_record)}
                else:
                    return {"is_exist": False}

        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise

    async def add_category_to_product(self, product_id: int, category_id: int):
        async with self.db.begin:
            stmt = select(ProductCategory).where(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id
            )
            result = await self.db.execute(stmt)
            try:
                link = result.scalar_one()
                return {"message": "This category is already linked to the product."}
            except NoResultFound:
                new_association = ProductCategory(
                    product_id=product_id,
                    category_id=category_id
                )
                self.db.add(new_association)
                await self.db.commit()
                return {"message": "Category added to the product successfully."}

    async def add_new_category(self, category: Category):
        try:
            self.db.add(category)
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise

