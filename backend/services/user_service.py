import logging
from datetime import datetime, timezone
from uuid import UUID
from typing import List
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import User, Cart
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict
from dependencies import send_verification_email, verify_code, hash_password
from schemas.schemas import UserCreate

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class UserService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: UUID) -> dict:
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found",
                )
            await self.db.refresh(user)
            return db_model_to_dict(user)
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_by_id: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def get_all_users(self) -> list[dict]:
        try:
            result = await self.db.execute(select(User))
            users = result.scalars().all()
            for user in users:
                await self.db.refresh(user)
            return [db_model_to_dict(user) for user in users] if users else []
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_users: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def get_users_by_type(self, is_seller: bool) -> list[dict]:
        try:
            result = await self.db.execute(
                select(User).where(User.is_seller == is_seller)
            )
            users = result.scalars().all()
            return [db_model_to_dict(user) for user in users] if users else []
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_users_by_role: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def get_user_by_email(self, email: str) -> dict:
        try:
            stmt = select(User).filter(User.email == email)
            result = await self.db.execute(stmt)
            user: User = result.scalars().first()

            if not user:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found",
                )

            return db_model_to_dict(user) if user else {}

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_by_email: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def check_seller_exists(self, seller_id: UUID) -> bool:
        try:
            stmt = select(User).filter(User.id == seller_id, User.is_seller)
            result = await self.db.execute(stmt)
            seller = result.scalar_one_or_none()

            if seller is None:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seller with ID {seller_id} not found",
                )
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error in check_seller_exists: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def create_new_user(self, user_data: UserCreate) -> str:
        try:
            user = User(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                hashed_password=hash_password(user_data.password),
                registration_date=datetime.now(timezone.utc).date(),
                is_seller=user_data.is_seller,
                password_length=len(user_data.password),
            )

            if not user_data.is_seller:
                user.cart = Cart(user=user)

            user_email = user_data.email
            user_first_name = user_data.first_name

            async with self.db.begin():
                self.db.add(user)
                await self.db.flush()
                await self.db.refresh(user)
                user_id = str(user.id)

            try:
                await send_verification_email(user_first_name, user_email)
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")
            return user_id

        except SQLAlchemyError as e:
            logger.error(f"Database error in create_new_user: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when creating the user",
            )

    async def verify_email(self, email, code):
        try:
            is_verified, message = await verify_code(email, code)
            if not is_verified:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=message
                )
            else:
                await self.update_is_verified_column(email)
        except SQLAlchemyError as e:
            logger.error(f"Database error in verify_email: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def search_sellers(self, query: str) -> List[dict]:
        if not query or len(query.strip()) == 0:
            raise UserException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Search query cannot be empty",
            )
        try:
            try:
                seller_uuid = UUID(query)
            except ValueError:
                seller_uuid = None

            stmt = select(User).where(
                or_(
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%"),
                    User.id == seller_uuid,
                )
            )
            result = await self.db.execute(stmt)
            sellers = result.scalars().all()

            return [db_model_to_dict(seller) for seller in sellers]

        except SQLAlchemyError as e:
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            ) from e

    async def update_is_verified_column(self, email: str) -> dict:
        try:
            stmt = select(User).filter(User.email == email)
            result = await self.db.execute(stmt)
            user: User = result.scalars().first()

            if not user:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found",
                )

            user.is_verified = True
            await self.db.flush()
            await self.db.refresh(user)

            return {
                "id": str(user.id),
                "email": user.email,
                "is_verified": user.is_verified,
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error in search_sellers: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def edit_user(self, user_id: UUID, update_data: dict) -> dict:
        try:
            stmt = select(User).filter(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found",
                )

            valid_fields = UserCreate.model_fields.keys()
            invalid_fields = [
                field for field in update_data.keys() if field not in valid_fields
            ]

            if invalid_fields:
                raise UserException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid fields: {', '.join(invalid_fields)}",
                )

            for key, value in update_data.items():
                setattr(user, key, value)

            await self.db.flush()
            await self.db.refresh(user)
            return db_model_to_dict(user)

        except SQLAlchemyError as e:
            logger.error(f"Database error in edit_user: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )

    async def delete_user(self, user_id: UUID) -> str:
        try:

            stmt = select(User).filter(User.id == user_id)
            result = await self.db.execute(stmt)
            user: User | None = result.scalars().first()

            if user is None:
                raise UserException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found",
                )

            await self.db.delete(user)
            await self.db.flush()

            return str(user_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error in delete_user: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database",
            )
