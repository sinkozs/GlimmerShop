from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import UUID
from dependencies import dict_to_db_model, db_model_to_dict
from services.organizer_service import OrganizerService
from models.models import User, Cart, Organizer
from config.auth_config import bcrypt_context
from schemas.schemas import UserCreate, UserUpdate
from datetime import datetime, timezone
from exceptions.user_exceptions import UserException
from fastapi import HTTPException


class OrganizerController:

    def __init__(self, organizer_service: OrganizerService):
        self._service = organizer_service

    async def get_organizer_by_id(self, organizer_id: UUID) -> dict:
        try:
            organizer_model = await self._service.get_organizer_by_id(organizer_id)
            return organizer_model
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_organizers(self):
        try:
            return await self._service.get_all_organizers()
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def create_new_organizer(self, organizer: UserCreate):
        organizer_model = Organizer()
        organizer_model.first_name = organizer.first_name
        organizer_model.last_name = organizer.last_name
        organizer_model.email = organizer.email
        organizer_model.hashed_password = self.hash_password(organizer.password)
        organizer_model.registration_date = datetime.now(timezone.utc).date()
        organizer_model.is_organizer = True

        try:
            await self._service.create_new_organizer(organizer_model)

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_organizer(self, organizer_id: UUID, organizer_update: UserUpdate):
        original_organizer: Organizer = dict_to_db_model(Organizer, await self.get_organizer_by_id(organizer_id))
        if original_organizer:
            if organizer_update.is_valid_update(organizer_update.first_name, original_organizer.first_name):
                original_organizer.first_name = organizer_update.first_name
            if organizer_update.is_valid_update(organizer_update.last_name, original_organizer.last_name):
                original_organizer.last_name = organizer_update.last_name
            if organizer_update.is_valid_update(organizer_update.email, original_organizer.email):
                original_organizer.email = organizer_update.email
            if not bcrypt_context.verify(organizer_update.password, original_organizer.hashed_password):
                original_organizer.hashed_password = self.hash_password(organizer_update.password)

        try:
            await self._service.edit_organizer(original_organizer)

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_organizer_by_email(self, email: EmailStr):
        try:
            return await self._service.get_organizer_by_email(email)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt_context.hash(password)

    async def delete_organizer(self, organizer_id):
        try:
            await self._service.delete_organizer(organizer_id)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
