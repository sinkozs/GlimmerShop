from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Response
from controllers.auth_controller import AuthController
from pydantic import EmailStr
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserService
from dependencies import get_current_user

from models.database import get_redis

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify-pw")
def verify_password(password1, password2,
                session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return auth_controller.verify_password(password1, password2)
    except HTTPException as e:
        raise e


@router.post("/login")
async def login(is_seller: bool, response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session), redis: aioredis.Redis = Depends(get_redis)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        return await auth_controller.login_for_access_token(is_seller, response, redis, form_data)
    except HTTPException as e:
        raise e


@router.post("/logout")
async def user_logout(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    try:
        user_id: UUID = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        return await auth_controller.user_logout(user_id)
    except HTTPException as e:
        raise e


@router.post("/forgotten-password")
async def regenerate_forgotten_password(email: EmailStr, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    auth_controller = AuthController(service)
    print(f"email: {email}, type: {type(email)}")
    try:
        return await auth_controller.regenerate_forgotten_password(email)
    except HTTPException as e:
        raise e
