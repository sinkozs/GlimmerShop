from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import UUID

from dependencies import dict_to_db_model, db_model_to_dict, is_valid_update, hash_password
from services.user_service import UserService
from models.models import User, Cart
from config.auth_config import bcrypt_context
from schemas.schemas import UserCreate, UserUpdate
from datetime import datetime, timezone
from exceptions.user_exceptions import UserException
from fastapi import HTTPException


class UserController:

    def __init__(self, user_service: UserService):
        self._service = user_service

    async def get_user_by_id(self, user_id: UUID) -> dict:
        try:
            user_model = await self._service.get_user_by_id(user_id)
            return user_model
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_all_users(self):
        try:
            return await self._service.get_all_users()
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_users_by_role(self, is_seller: bool):
        try:
            return await self._service.get_users_by_role(is_seller)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def create_new_user(self, user: UserCreate):
        user_model = User()
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.email = user.email
        user_model.hashed_password = self.hash_password(user.password)
        user_model.registration_date = datetime.now(timezone.utc).date()
        user_model.is_seller = user.is_seller

        if not user.is_seller:
            user_model.cart = Cart(user=user_model)

        try:
            await self._service.create_new_user(user_model)
            await self._service.send_email_to_user(user_model)

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def verify_user(self, email, code):
        try:
            await self._service.verify_email(email, code)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_user(self, user_id: UUID, user_update: UserUpdate):
        original_user: User = dict_to_db_model(User, await self.get_user_by_id(user_id))
        if original_user:
            if is_valid_update(user_update.first_name, original_user.first_name):
                original_user.first_name = user_update.first_name
            if is_valid_update(user_update.last_name, original_user.last_name):
                original_user.last_name = user_update.last_name
            if is_valid_update(user_update.email, original_user.email):
                original_user.email = user_update.email
            if user_update.password:
                if not bcrypt_context.verify(user_update.password, original_user.hashed_password):
                    original_user.hashed_password = hash_password(user_update.password)
        try:
            await self._service.edit_user(original_user)

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_user_by_email(self, email: EmailStr):
        try:
            return await self._service.get_user_by_email(email)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_user(self, user_id: UUID):
        try:
            await self._service.delete_user(user_id)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

