import json
from typing import List

from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import UUID

from dependencies import dict_to_db_model, is_valid_update, hash_password, send_verification_email
from services.user_service import UserService
from models.models import User, Cart
from config.auth_config import bcrypt_context
from schemas.schemas import UserCreate, UserUpdate, UserQuery, UserVerification
from schemas.response_schemas import UserResponse
from datetime import datetime, timezone
from exceptions.user_exceptions import UserException
from fastapi import HTTPException, Query, status
from fastapi.responses import JSONResponse


class UserController:

    def __init__(self, user_service: UserService):
        self._service = user_service

    async def get_user_by_id(self, user_id: UUID) -> JSONResponse:
        try:
            user: dict = await self._service.get_user_by_id(user_id=user_id)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"user": UserResponse.model_validate(user).model_dump()}
            )
        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            )

    async def get_all_users(self) -> JSONResponse:
        try:
            users = await self._service.get_all_users()
            print(users)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "users": [
                        UserResponse.model_validate(user).model_dump()
                        for user in users
                    ]
                }
            )
        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e

    async def get_users_by_type(self,
                                is_seller: bool = Query(..., description="True for sellers, False for customers")):
        try:
            return await self._service.get_users_by_role(is_seller)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def check_if_seller_exists(self, seller_id: UUID) -> JSONResponse:
        try:
            exists = await self._service.check_seller_exists(seller_id)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"exists": exists}
            )
        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            )

    async def search_sellers(self, query: str = Query(...)) -> List[UserQuery]:
        try:
            return await self._service.search_sellers(query)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def create_new_user(self, user_data: UserCreate) -> JSONResponse:
        try:
            user_id = await self._service.create_new_user(user_data)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"userId": user_id}
            )
        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e

    async def verify_user(self, verification: UserVerification) -> JSONResponse:
        try:
            await self._service.verify_email(verification.email, verification.code)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "User verified successfully",
                    "email": verification.email
                }
            )
        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e

    async def resend_verification_email(self, email: str) -> JSONResponse:
        try:
            user = await self._service.get_user_by_email(email)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if user["is_verified"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is already verified!"
                )

            email_sent = await send_verification_email(user["first_name"], user["email"])

            if email_sent:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Verification email sent successfully"}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email"
                )

        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e

    async def edit_user(self, user_id: UUID, user_update: UserUpdate) -> JSONResponse:
        try:
            current_user = await self._service.get_user_by_id(user_id)

            update_data = {}
            if is_valid_update(user_update.first_name, current_user["first_name"]):
                update_data["first_name"] = user_update.first_name
            if is_valid_update(user_update.last_name, current_user["last_name"]):
                update_data["last_name"] = user_update.last_name
            if is_valid_update(user_update.email, current_user["email"]):
                update_data["email"] = user_update.email

            if user_update.password:
                if not bcrypt_context.verify(
                        user_update.password,
                        current_user["hashed_password"]
                ):
                    update_data["hashed_password"] = hash_password(user_update.password)

            if update_data:
                updated_user = await self._service.edit_user(user_id, update_data)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=updated_user
                )

            return JSONResponse(
                status_code=status.HTTP_304_NOT_MODIFIED,
                content=current_user
            )

        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e

    async def get_user_by_email(self, email: EmailStr):
        try:
            return await self._service.get_user_by_email(email)
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_user(self, user_id: UUID) -> JSONResponse:
        try:
            result = await self._service.delete_user(user_id)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": result["message"],
                    "user_id": result["user_id"]
                }
            )

        except UserException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e.detail)
            ) from e
