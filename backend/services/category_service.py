from typing import List

from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import Product, Category, ProductCategory
from sqlalchemy.orm import selectinload
from sqlalchemy import or_

from exceptions.category_exceptions import CategoryException
from exceptions.product_exceptions import ProductException
from exceptions.user_exceptions import UserException
from dependencies import (
    db_model_to_dict,
    convert_str_to_int_if_numeric,
    is_valid_update,
)
from schemas.schemas import CategoryUpdate, CategoryQuery


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
                    raise CategoryException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No categories found!",
                    )
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_product_categories(self, product_id: int) -> list:
        try:
            async with self.db.begin():
                stmt = (
                    select(Product)
                    .options(
                        selectinload(Product.product_category).selectinload(
                            ProductCategory.category
                        )
                    )
                    .where(Product.id == product_id)
                )

                result = await self.db.execute(stmt)
                product = result.scalars().one_or_none()

                if product is None:
                    raise ProductException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product with id {product_id} not found!",
                    )
                product_categories = [
                    {pc.category.id: pc.category.category_name}
                    for pc in product.product_category
                ]
                return product_categories
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def search_categories(self, query: str) -> List[CategoryQuery]:
        async with self.db.begin():
            try:
                category_id = int(query)
            except ValueError:
                category_id = None

            stmt = select(Category).where(
                or_(
                    Category.category_name.ilike(f"%{query}%"),
                    Category.id == category_id,
                )
            )

            result = await self.db.execute(stmt)
            categories = result.scalars().all()

            return [CategoryQuery.model_validate(category) for category in categories]

    async def get_products_by_category(self, category_id: int) -> list:
        try:
            async with self.db.begin():
                stmt = (
                    select(Category)
                    .options(
                        selectinload(Category.product_category).selectinload(
                            ProductCategory.product
                        )
                    )
                    .where(Category.id == category_id)
                )

                result = await self.db.execute(stmt)
                category = result.scalars().one_or_none()

                if category is None:
                    raise CategoryException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Category with id {category_id} not found!",
                    )

                products_list = [
                    {
                        "id": pc.product.id,
                        "seller_id": pc.product.seller_id,
                        "name": pc.product.name,
                        "description": pc.product.description,
                        "price": pc.product.price,
                        "stock_quantity": pc.product.stock_quantity,
                        "material": pc.product.material,
                        "color": pc.product.color,
                        "image_path": pc.product.image_path,
                        "image_path2": pc.product.image_path2,
                    }
                    for pc in category.product_category
                ]
                return products_list
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def check_category_exists(self, category_identifier: str) -> dict:
        try:
            category_identifier = convert_str_to_int_if_numeric(category_identifier)
            async with self.db.begin():
                # the identifier is the id
                if isinstance(category_identifier, int):
                    condition = Category.id == category_identifier
                    # the identifier is the category name
                elif isinstance(category_identifier, str):
                    condition = Category.category_name == category_identifier
                else:
                    raise ValueError("Invalid category identifier type")

                stmt = select(Category).where(condition)
                result = await self.db.execute(stmt)
                category_record = result.scalar_one_or_none()
                if category_record:
                    return {
                        "is_exist": True,
                        "category_record": db_model_to_dict(category_record),
                    }
                else:
                    return {"is_exist": False}
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def add_category_to_product(self, product_id: int, category_id: int):
        try:
            stmt = select(ProductCategory).where(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
            )
            result = await self.db.execute(stmt)
            link = result.scalar_one_or_none()

            if link:
                return {"message": "This category is already linked to the product."}

            new_association = ProductCategory(
                product_id=product_id, category_id=category_id
            )
            self.db.add(new_association)

            await self.db.commit()
            return {"message": "Category added to the product successfully."}

        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database.",
            )

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
            async with self.db.begin():
                stmt = select(ProductCategory).where(
                    ProductCategory.product_id == product_id,
                    ProductCategory.category_id == category_id,
                )
                product_category: ProductCategory = await self.db.scalar(stmt)

                if not product_category:
                    raise ProductException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No link between category ID {category_id} and product ID {product_id} was found.",
                    )

                await self.db.delete(product_category)
                await self.db.flush()
                return {"message": f"Product Category link successfully deleted!"}
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def add_new_category(self, category_name: str) -> int:
        try:
            category = Category()
            category.category_name = category_name.lower()
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(instance=category, attribute_names=["id"])
            print(f"new category id: {category.id}")
            return category.id
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def edit_category(self, category_id: int, category_update: CategoryUpdate):
        async with self.db.begin():
            stmt = select(Category).where(Category.id == category_id)
            result = await self.db.execute(stmt)
            category: Category = result.scalars().first()

            if category is None:
                raise ProductException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No category found with id {category_id}",
                )
            if is_valid_update(category_update.category_name, category.category_name):
                category.category_name = category_update.category_name
            if is_valid_update(
                category_update.category_description, category.category_description
            ):
                category.category_description = category_update.category_description
            self.db.add(category)
            await self.db.commit()
