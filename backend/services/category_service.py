from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status

from config.logger_config import get_logger
from models.models import Product, Category, ProductCategory
from sqlalchemy.orm import selectinload
from sqlalchemy import or_

from exceptions.category_exceptions import CategoryException
from exceptions.product_exceptions import ProductException
from dependencies import (
    db_model_to_dict,
    is_valid_update,
)
from schemas.schemas import CategoryUpdate, CategoryQuery, CategoryIdentifiers


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.logger = get_logger(__name__)

    async def get_all_categories(self) -> List[dict]:
        try:
            result = await self.db.execute(select(Category))
            categories = result.scalars().all()
            if categories:
                return [db_model_to_dict(c) for c in categories]
            return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_all_categories: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_category_name_by_id(self, category_id: int) -> dict:
        try:
            stmt = select(Category).where(Category.id == category_id)
            result = await self.db.execute(stmt)
            category: Category = result.scalar_one_or_none()

            if not category:
                raise CategoryException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {category_id} not found",
                )
            await self.db.commit()
            await self.db.refresh(category)
            return {"category_name": category.category_name}
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_category_name_by_id: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def get_product_categories(self, product_id: int) -> list:
        try:
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
            if product.product_category:
                product_categories = [pc.id for pc in product.product_category]
                return product_categories
            return []
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_product_categories: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def search_categories(self, query: str) -> List[CategoryQuery]:
        try:
            category_id = int(query)
        except ValueError:
            category_id = None

        try:
            stmt = select(Category).where(
                or_(
                    Category.category_name.ilike(f"%{query}%"),
                    Category.id == category_id,
                )
            )

            result = await self.db.execute(stmt)
            categories = result.scalars().all()
            if not categories:
                return []
            return [CategoryQuery.model_validate(category) for category in categories]
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in search_categories: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_products_by_category(self, category_id: int) -> list:
        try:
            stmt = (
                select(Category)
                .where(Category.id == category_id)
                .options(
                    selectinload(Category.product_category).selectinload(
                        ProductCategory.product
                    )
                )
            )

            result = await self.db.execute(stmt)
            category = result.unique().scalar_one_or_none()

            if category is None:
                raise CategoryException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {category_id} not found!",
                )

            return [
                {
                    "id": product.product.id,
                    "seller_id": product.product.seller_id,
                    "name": product.product.name,
                    "description": product.product.description,
                    "price": product.product.price,
                    "stock_quantity": product.product.stock_quantity,
                    "material": product.product.material,
                    "color": product.product.color,
                    "image_path": product.product.image_path,
                    "image_path2": product.product.image_path2,
                }
                for product in category.product_category
            ]

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_products_by_category: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def check_category_exists(
        self, category_identifier: CategoryIdentifiers
    ) -> dict:
        try:
            conditions = []
            if category_identifier.category_id is not None:
                conditions.append(Category.id == category_identifier.category_id)
            if category_identifier.category_name is not None:
                conditions.append(
                    Category.category_name == category_identifier.category_name
                )

            if not conditions:
                raise ValueError("No valid category identifier provided")

            stmt = select(Category).where(or_(*conditions))

            result = await self.db.execute(stmt)
            category_record: Category = result.scalar_one_or_none()

            if category_record:
                return db_model_to_dict(category_record)

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in check_category_exists: {e}")
            raise CategoryException(
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
            self.logger.error(f"Database error in add_category_to_product: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database.",
            )

    async def delete_category_from_product(self, product_id: int, category_id: int):
        try:
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
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in delete_category_from_product: {e}")
            raise CategoryException(
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
            return category.id
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in add_new_category: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def edit_category(self, category_id: int, category_update: CategoryUpdate):
        try:
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
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in edit_category: {e}")
            raise CategoryException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )
