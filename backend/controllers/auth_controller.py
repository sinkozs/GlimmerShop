from fastapi import Depends, HTTPException
from exceptions.auth_exceptions import AuthenticationException
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm


class AuthController:
    def __init__(self, service: AuthService):
        self._service = service

    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
        try:
            email = form_data.username
            password = form_data.password
            user = await self._service.authenticate_user(email, password)
            token = self._service.create_user_token(user)
            return {"user_token": token, "user_id": user["id"]}
        except AuthenticationException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def user_logout(self, user: dict):
        await self._service.user_logout(user)
