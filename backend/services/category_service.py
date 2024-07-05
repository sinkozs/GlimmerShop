from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from sqlalchemy import func, and_
from models.models import Product, User, Category, ProductCategory
from sqlalchemy.orm import joinedload, selectinload

from exceptions.category_exceptions import CategoryException
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
                    raise CategoryException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"No categories found!")
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_product_categories(self, product_id: int) -> list:
        try:
            async with self.db.begin():
                stmt = select(Product).options(
                    selectinload(Product.product_category).selectinload(ProductCategory.category)
                ).where(Product.id == product_id)

                result = await self.db.execute(stmt)
                product = result.scalars().one_or_none()

                if product is None:
                    raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                           detail=f"Product with id {product_id} not found!")
                category_names = [pc.category.category_name for pc in product.product_category]
                return category_names
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def get_products_by_category(self, category_id: int) -> list:
        try:
            async with self.db.begin():
                stmt = select(Category).options(
                    selectinload(Category.product_category).selectinload(ProductCategory.product)
                ).where(Category.id == category_id)

                result = await self.db.execute(stmt)
                category = result.scalars().one_or_none()

                if category is None:
                    raise CategoryException(status_code=status.HTTP_404_NOT_FOUND,
                                            detail=f"category with id {category_id} not found!")
                products_list = [pc.product.name for pc in category.product_category]
                return products_list
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail="An error occurred when accessing the database!")

    async def check_category_exists(self, category_identifier: str) -> dict:
        try:
            category_identifier = convert_str_to_int_if_numeric(category_identifier)
            async with self.db.begin():
                # the identifier is the id
                if isinstance(category_identifier, int):
                    condition = (Category.id == category_identifier)
                    # the identifier is the category name
                elif isinstance(category_identifier, str):
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
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def add_category_to_product(self, product_id: int, category_id: int):
        try:
            async with self.db.begin():
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
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
            async with self.db.begin():
                stmt = select(ProductCategory).where(
                    ProductCategory.product_id == product_id,
                    ProductCategory.category_id == category_id
                )
                product_category: ProductCategory = await self.db.scalar(stmt)

                if not product_category:
                    raise ProductException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"No link between category ID {category_id} and product ID {product_id} was found.")

                await self.db.delete(product_category)
                await self.db.flush()
                return {"message": f"Product Category link successfully deleted!"}
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def add_new_category(self, category: Category):
        try:
            self.db.add(category)
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

