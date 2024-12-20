from pydantic import EmailStr
from uuid import UUID
import dependencies
from dependencies import is_valid_update, hash_password
from services.user_service import UserService
from config.auth_config import bcrypt_context
from schemas.schemas import UserCreate, UserUpdate, UserVerification
from schemas.response_schemas import UserResponse
from exceptions.user_exceptions import UserException
from fastapi import HTTPException, Query, status


class UserController:

    def __init__(self, user_service: UserService):
        self._service = user_service

    async def get_user_by_id(self, user_id: str) -> dict:
        try:
            user: dict = await self._service.get_user_by_id(user_id=UUID(user_id))
            return UserResponse.model_validate(user).model_dump()
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    async def get_all_users(self) -> list[dict]:
        try:
            users = await self._service.get_all_users()
            return [UserResponse.model_validate(user).model_dump() for user in users]
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_users_by_type(
        self,
        is_seller: bool = Query(
            ..., description="True for sellers, False for customers"
        ),
    ) -> list[dict]:
        try:
            users = await self._service.get_users_by_type(is_seller)
            return [UserResponse.model_validate(user).model_dump() for user in users]
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def get_user_by_email(self, email: EmailStr) -> dict:
        try:
            user: dict = await self._service.get_user_by_email(email)
            return UserResponse.model_validate(user).model_dump()
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def check_seller_exists(self, seller_id: UUID) -> dict[str, bool]:
        try:
            exists = await self._service.check_seller_exists(seller_id)
            return {"exists": exists}
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    async def search_sellers(self, query: str) -> list[dict]:
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Search query cannot be empty or whitespace only",
            )

        try:
            sellers = await self._service.search_sellers(query)
            return [
                UserResponse.model_validate(seller).model_dump() for seller in sellers
            ]
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def create_new_user(self, user_data: UserCreate) -> dict[str, str]:
        try:
            user_id = await self._service.create_new_user(user_data)
            return {"user_id": user_id}
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def verify_user(self, verification: UserVerification) -> dict[str, bool]:
        try:
            await self._service.verify_email(verification.email, verification.code)
            return {"is_verified": True}
        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def resend_verification_email(self, email: str) -> dict[str, str]:
        try:
            user: dict = await self._service.get_user_by_email(email)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            if user["is_verified"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is already verified!",
                )

            email_sent = await dependencies.send_verification_email(
                user["first_name"], user["email"]
            )

            if email_sent:
                return {"email": email}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email",
                )

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def edit_user(self, user_id: UUID, user_update: UserUpdate) -> dict:
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
                    user_update.password, current_user["hashed_password"]
                ):
                    update_data["hashed_password"] = hash_password(user_update.password)

            if len(update_data) != 0:
                updated_user = await self._service.edit_user(user_id, update_data)
                return UserResponse.model_validate(updated_user).model_dump()
            return UserResponse.model_validate(current_user).model_dump()

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def delete_user(self, user_id: UUID) -> dict[str, str]:
        try:
            result = await self._service.delete_user(user_id)
            return {"user_id": result}

        except UserException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
