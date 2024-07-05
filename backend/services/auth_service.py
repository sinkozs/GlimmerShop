import json
import os

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from typing import Optional
from pydantic import EmailStr
from fastapi import status, Response, Request
from jose import jwt
import secrets
import string
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from models.models import User
from config.auth_config import ALGORITHM, bcrypt_context
from services.user_service import UserService
from exceptions.auth_exceptions import AuthenticationException
from dependencies import db_model_to_dict, send_password_reset_email, hash_password
from config.parser import load_config

from dependencies import generate_session_id


class AuthService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.auth_config = load_config().auth_config


    def verify_password(self, plain_password, hashed_password) -> bool:
        return bcrypt_context.verify(plain_password, hashed_password)

    def generate_strong_password(self) -> str:
        length = self.auth_config.min_password_length
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # ensuring the password includes at least one lowercase, one uppercase, one digit, and one special character
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(length))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c in string.punctuation for c in password)):
                break

        return password

    def create_access_token(self, user_id: UUID, email: EmailStr, expires_delta: Optional[timedelta] = None) -> str:
        encode = {"id": str(user_id), "email": str(email)}
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=self.auth_config.token_expiry_minutes)
        encode.update({"exp": expire})
        return jwt.encode(encode, self.auth_config.secret_key, algorithm=ALGORITHM)

    async def get_redis_session(self, request: Request, response: Response, redis: aioredis.Redis) -> str:
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = generate_session_id()
            response.set_cookie(key="session_id", value=session_id)
        return session_id

    async def create_redis_session(self, response: Response, redis: aioredis.Redis, user_id: Optional[UUID] = None) -> str:
        session_id = generate_session_id()
        session_data = {"user_id": str(user_id)} if user_id else {}
        await redis.set(session_id, json.dumps(session_data))
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, samesite='Lax')
        return session_id
        
    def create_user_token(self, user: dict):
        cfg = load_config()
        user_token_expires = timedelta(minutes=self.auth_config.token_expiry_minutes)
        return self.create_access_token(user["id"], user["email"], expires_delta=user_token_expires)

    async def authenticate_user(self, email: EmailStr, password: str) -> dict:
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


    async def regenerate_forgotten_password(self, user_email: EmailStr):
        async with self.db.begin():
            stmt = select(User).filter(User.email == user_email)
            result = await self.db.execute(stmt)
            user_model = result.scalars().first()
            if user_model:
                new_password = self.generate_strong_password()
                user_model.hashed_password = hash_password(new_password)
                self.db.add(user_model)
                await self.db.commit()
                await send_password_reset_email(user_email, new_password)
            if not user_model:
                raise AuthenticationException()

    async def user_logout(self, user_id: UUID):
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.id == user_id)
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()
                if user_model and user_model.is_active:
                    user_model.is_active = False
                    await self.db.commit()

        except SQLAlchemyError:
            raise AuthenticationException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                          detail="An error occurred when accessing the database!")
