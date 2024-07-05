from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Response
from exceptions.auth_exceptions import AuthenticationException
from pydantic import EmailStr
from services.auth_service import AuthService
from services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm


class AuthController:
    def __init__(self, service: AuthService):
        self._service = service

    async def login_for_access_token(self, response: Response, redis: aioredis.Redis, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
        email = form_data.username
        password = form_data.password
        user = await self._service.authenticate_user(email, password)
        token = self._service.create_user_token(user)
        if user:
            user_id = user["id"]
            session_id = await self.get_redis_session(response, redis, user_id)
            return {"user_token": token, "user_id": user_id, "session_id": session_id}

    async def get_redis_session(self, response: Response, redis: aioredis.Redis, user_id: Optional[UUID] = None):
        session_id = await self._service.create_redis_session(response, redis, user_id)
        print(f"controller: get_redis_session session_id {session_id}")
        return session_id

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

    async def regenerate_forgotten_password(self, user_email: EmailStr):
        try:
            return await self._service.regenerate_forgotten_password(user_email)
        except AuthenticationException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail)) from e