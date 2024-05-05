from uuid import UUID
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from models.models import User, Organizer
from exceptions.user_exceptions import UserException
from dependencies import db_model_to_dict


class OrganizerService:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_organizer_by_id(self, organizer_id: UUID) -> dict:
        try:
            async with self.db.begin():
                stmt = select(Organizer).filter(Organizer.id == organizer_id)
                result = await self.db.execute(stmt)
                organizer_model: Organizer = result.scalars().first()
                if organizer_model:
                    return db_model_to_dict(organizer_model)
                else:
                    raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Organizer with id {organizer_id} not found!")
        except SQLAlchemyError:
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def get_all_organizers(self) -> List[dict]:
        try:
            async with self.db.begin():
                result = await self.db.execute(select(Organizer))
                organizer_model = result.scalars().all()
                if organizer_model:
                    organizer_data = [db_model_to_dict(organizer) for organizer in organizer_model]
                    return organizer_data
                else:
                    raise UserException()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def get_organizer_by_email(self, email: str):
        try:
            async with self.db.begin():
                stmt = select(Organizer).filter(Organizer.email == email)
                result = await self.db.execute(stmt)
                organizer_model: Organizer = result.scalars().first()
                if organizer_model:
                    return organizer_model
                else:
                    return None
        except SQLAlchemyError:
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def create_new_organizer(self, organizer: Organizer):
        try:
            async with self.db.begin():
                self.db.add(organizer)
                await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def edit_organizer(self, edited_organizer: Organizer):
        try:
            async with self.db.begin():
                await self.db.merge(edited_organizer)
                await self.db.commit()

        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")

    async def delete_organizer(self, organizer_id: UUID):
        try:
            async with self.db.begin():
                stmt = select(Organizer).filter(Organizer.id == organizer_id)
                result = await self.db.execute(stmt)
                organizer_model = result.scalars().first()

            if organizer_model is not None:
                await self.db.delete(organizer_model)
            else:

                raise UserException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Organizer with {organizer_id} id not found!")
            await self.db.commit()
        except SQLAlchemyError as e:
            print(f"Database access error: {e}")
            raise UserException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred when accessing the database!")
