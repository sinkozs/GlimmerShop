from fastapi import Depends, HTTPException, Response, status
from exceptions.auth_exceptions import AuthenticationException
from pydantic import EmailStr
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm


class AuthController:
    def __init__(self, service: AuthService):
        self._service = service

    async def login_for_access_token(
            self,
            is_seller: bool,
            response: Response,
            form_data: OAuth2PasswordRequestForm = Depends(),
    ) -> dict:
        email = form_data.username
        password = form_data.password

        if not is_seller:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only sellers can login through this endpoint."
            )

        try:
            seller = await self._service.authenticate_seller(email, password)
            if not seller:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            response = await self._service.set_response_cookie(
                seller["id"],
                seller["email"],
                response
            )

            return {
                "response": response,
                "seller_id": seller["id"]
            }

        except AuthenticationException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e.detail)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )

    async def user_logout(self, user: dict):
        try:
            return await self._service.user_logout(user)
        except AuthenticationException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    def verify_password(self, password1, password2):
        try:
            return self._service.verify_password(password1, password2)
        except AuthenticationException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e

    async def regenerate_forgotten_password(self, email: EmailStr):
        try:
            return await self._service.regenerate_forgotten_password(email)
        except AuthenticationException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e
