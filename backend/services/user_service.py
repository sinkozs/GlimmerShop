from uuid import UUID
from typing import List
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import User
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict
from dependencies import send_verification_email, verify_code
from schemas.schemas import UserQuery


class UserService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: UUID) -> dict:
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.id == user_id)
                result = await self.db.execute(stmt)
                user_model: User = result.scalars().first()
                if user_model:
                    return db_model_to_dict(user_model)
                else:
                    raise UserException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with id {user_id} not found!",
                    )
        except SQLAlchemyError:
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_all_users(self) -> List[dict]:
        try:
            async with self.db.begin():
                result = await self.db.execute(select(User))
                users_model = result.scalars().all()
                if users_model:
                    users_data = [db_model_to_dict(user) for user in users_model]
                    return users_data
                else:
                    raise UserException()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_users_by_role(self, is_seller: bool) -> List[dict]:
        try:
            async with self.db.begin():
                result = await self.db.execute(
                    select(User).where(User.is_seller == is_seller)
                )
                sellers_model = result.scalars().all()
                if sellers_model:
                    users_data = [db_model_to_dict(user) for user in sellers_model]
                    return users_data
                else:
                    raise UserException()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def get_user_by_email(self, email: str):
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.email == email)
                result = await self.db.execute(stmt)
                user_model: User = result.scalars().first()
                if user_model:
                    return user_model
                else:
                    raise UserException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No user found with email {email}",
                    )
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def check_seller_exists(self, seller_id: UUID) -> bool:
        try:
            async with self.db.begin():
                stmt = select(func.count()).where(
                    and_(User.id == seller_id, User.is_seller == True)
                )
                result = await self.db.execute(stmt)
                return result.scalar_one() > 0
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def create_new_user(self, user: User):
        try:
            async with self.db.begin():
                self.db.add(user)
                await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def send_email_to_user(self, user: User):
        async with self.db.begin():
            await self.db.refresh(
                instance=user,
                attribute_names=["id", "first_name", "last_name", "email"],
            )
            await send_verification_email(user.first_name, user.email)

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
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def search_sellers(self, query: str) -> List[UserQuery]:
        async with self.db.begin():
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

            return [UserQuery.model_validate(seller) for seller in sellers]

    async def update_is_verified_column(self, email):
        try:
            user: User = await self.get_user_by_email(email)
            user.is_verified = True
            self.db.add(user)
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def edit_user(self, edited_user: User):
        try:
            async with self.db.begin():
                await self.db.merge(edited_user)
                await self.db.commit()

        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def delete_user(self, user_id: UUID):
        async with self.db.begin():
            stmt = select(User).filter(User.id == user_id)
            result = await self.db.execute(stmt)
            user_model: User = result.scalars().first()

        if user_model is not None:
            await self.db.delete(user_model)
            await self.db.commit()

        else:
            raise UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with {user_id} id not found!",
            )
