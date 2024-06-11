import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from typing import Optional
from pydantic import EmailStr
from fastapi import status
from jose import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

from models.models import User
from config.auth_config import ALGORITHM, bcrypt_context
from services.user_service import UserService
from exceptions.auth_exceptions import AuthenticationException
from dependencies import db_model_to_dict
from config.parser import load_config


class AuthService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.auth_config = load_config().auth_config

    def verify_password(self, plain_password, hashed_password) -> bool:
        return bcrypt_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: UUID, email: EmailStr, expires_delta: Optional[timedelta] = None) -> str:
        encode = {"id": str(user_id), "email": str(email)}
        print(
            f"TOKEN EXP MINS: {self.auth_config.token_expiry_minutes} Type: {type(self.auth_config.token_expiry_minutes)}")
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=self.auth_config.token_expiry_minutes)
        encode.update({"exp": expire})
        return jwt.encode(encode, self.auth_config.secret_key, algorithm=ALGORITHM)

    def create_user_token(self, user: dict):
        cfg = load_config()
        print(
            f"POSTGRES PORT: {cfg.db_config.port} Type: {type(cfg.db_config.port)}")
        print(f"TOKEN EXP MINS: {self.auth_config.token_expiry_minutes} Type: {type(self.auth_config.token_expiry_minutes)}")
        user_token_expires = timedelta(minutes=self.auth_config.token_expiry_minutes)
        return self.create_access_token(user["id"], user["email"], expires_delta=user_token_expires)

    async def authenticate_user(self, email: EmailStr, password: str) -> dict:
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.email == email)
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()
                if user_model:
                    user_dict = db_model_to_dict(user_model)

                if not user_model or not self.verify_password(password, user_model.hashed_password):
                    raise AuthenticationException()

                user_model.is_active = True
                user_model.last_login = datetime.now()
                self.db.add(user_model)
                await self.db.commit()
                return user_dict
        except SQLAlchemyError:
            raise AuthenticationException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                          detail="An error occurred when accessing the database!")

    async def user_logout(self, user: dict):
        try:
            async with self.db.begin():
                user_id: UUID = user.get("id")
                stmt = select(User).filter(User.id == user_id)
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()
                if user_model and user_model.is_active:
                    user_model.is_active = False
                    await self.db.commit()

        except SQLAlchemyError:
            raise AuthenticationException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                          detail="An error occurred when accessing the database!")
