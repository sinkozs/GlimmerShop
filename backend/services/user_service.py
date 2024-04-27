from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import User
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict


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
                    raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"User with id {user_id} not found!")
        except SQLAlchemyError:
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

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
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def get_user_by_email(self, email: str) -> User:
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.email == email)
                result = await self.db.execute(stmt)
                user_model: User = result.scalars().first()
                if user_model:
                    return user_model
                else:
                    raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"User with email address {email} not found!")
        except SQLAlchemyError:
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def create_new_user(self, user: User):
        try:
            async with self.db.begin():
                self.db.add(user)
                await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def edit_user(self, edited_user: User):
        try:
            async with self.db.begin():
                await self.db.merge(edited_user)
                await self.db.commit()

        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def delete_user(self, user_id: UUID):
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.id == user_id)
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()

            if user_model is not None:
                await self.db.delete(user_model)
            else:
                # Raise an exception or return a result indicating the user was not found
                raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"User with {user_id} id not found!")
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")
