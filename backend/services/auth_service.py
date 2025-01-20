from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from typing import Optional
from pydantic import EmailStr
from fastapi import status, Response
from jose import jwt
import secrets
import string
from datetime import datetime, timedelta
from uuid import UUID
from fastapi.responses import JSONResponse

import config
from config.logger_config import get_logger
from models.models import User
from config.auth_config import (
    bcrypt_context,
    jwt_algorithm,
    http_only_auth_cookie,
)
from exceptions.auth_exceptions import AuthenticationException
from dependencies import db_model_to_dict, send_password_reset_email, hash_password
from config.parser import load_config


class AuthService:

    def __init__(self, session: AsyncSession):
        self.db = session
        self.auth_config = load_config().auth_config
        self.logger = get_logger(__name__)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return bcrypt_context.verify(plain_password, hashed_password)

    def generate_strong_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # ensuring the password includes at least one lowercase, one uppercase, one digit, and one special character
        while True:
            password = "".join(
                secrets.choice(alphabet)
                for i in range(self.auth_config.min_password_length)
            )
            if (
                    any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c in string.punctuation for c in password)
            ):
                break

        return password

    def create_access_token(
            self, user_id: UUID, email: EmailStr, expires_delta: Optional[timedelta] = None
    ) -> str:
        encode = {"id": str(user_id), "email": str(email)}
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(
                minutes=self.auth_config.token_expiry_minutes
            )
        encode.update({"exp": expire})
        auth_config = load_config().auth_config
        private_key = auth_config.load_private_key().decode('utf-8')
        return jwt.encode(
            claims=encode, key=private_key, algorithm=jwt_algorithm
        )

    # async def get_redis_session(self, request: Request, response: Response) -> str:
    #     session_id = request.cookies.get("session_id")
    #     if not session_id:
    #         session_id = generate_session_id()
    #         response.set_cookie(key="session_id", value=session_id)
    #     return session_id

    # async def create_redis_session(
    #     self, response: Response, redis: aioredis.Redis, user_id: Optional[UUID] = None
    # ) -> str:
    #     session_id = generate_session_id()
    #     session_data = {"user_id": str(user_id)} if user_id else {}
    #     await redis.set(session_id, json.dumps(session_data))
    #     response.set_cookie(
    #         key="session_id",
    #         value=session_id,
    #         httponly=True,
    #         secure=True,
    #         samesite="Lax",
    #     )
    #     return session_id

    async def set_response_cookie(
            self,
            user_id: UUID,
            email: EmailStr,
            response: Response
    ) -> Response:
        access_token = self.create_access_token(user_id=user_id, email=email)

        response.set_cookie(
            key=http_only_auth_cookie,
            value=access_token,
            httponly=True,
            max_age=config.auth_config.token_expiry_minutes * 60,
            expires=config.auth_config.token_expiry_minutes * 60,
            samesite="lax",
            secure=False
        )

        return response

    async def authenticate(
            self, email: EmailStr, password: str, is_seller: bool
    ) -> dict:
        async with self.db.begin():
            try:
                user_type = "seller" if is_seller else "user"
                self.logger.info(
                    f"Attempting to authenticate {user_type} with email: {email}"
                )

                stmt = select(User).filter(
                    (User.email == email) & (User.is_seller == is_seller)
                )
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()

                if not user_model:
                    self.logger.warning(
                        f"Authentication failed: {user_type.capitalize()} not found with email: {email}"
                    )
                    raise AuthenticationException(
                        detail=f"{user_type.capitalize()} not found!"
                    )

                if not self.verify_password(password, user_model.hashed_password):
                    self.logger.warning(
                        f"Authentication failed: Invalid password for {user_type}: {email}"
                    )
                    raise AuthenticationException(detail="Invalid credentials!")

                user_dict = db_model_to_dict(user_model)
                user_model.is_active = True
                user_model.last_login = datetime.now()
                self.db.add(user_model)
                await self.db.commit()

                self.logger.info(
                    f"{user_type.capitalize()} successfully authenticated: {email}"
                )
                return user_dict

            except SQLAlchemyError as e:
                self.logger.error(
                    f"Database error during {user_type} authentication: {str(e)}",
                    extra={"email": email, "error_type": type(e).__name__},
                )
                raise AuthenticationException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred when accessing the database!",
                )

    async def authenticate_user(self, email: EmailStr, password: str) -> dict:
        return await self.authenticate(email, password, is_seller=False)

    async def authenticate_seller(self, email: EmailStr, password: str) -> dict:
        return await self.authenticate(email, password, is_seller=True)

    async def regenerate_forgotten_password(self, email: EmailStr):
        try:
            self.logger.info(f"Attempting to regenerate password for email: {email}")
            stmt = select(User).filter(User.email == email)
            result = await self.db.execute(stmt)
            user_model = result.scalars().first()

            if not user_model:
                self.logger.warning(
                    f"Password regeneration failed: User not found with email: {email}"
                )
                raise AuthenticationException()

            new_password = self.generate_strong_password()
            user_model.hashed_password = hash_password(new_password)
            self.db.add(user_model)
            await self.db.commit()

            await send_password_reset_email(email, new_password)
            self.logger.info(
                f"Password successfully regenerated and email sent for user: {email}"
            )

        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error during password regeneration: {str(e)}",
                extra={"email": email, "error_type": type(e).__name__},
            )
            raise AuthenticationException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )

    async def user_logout(self, user_id: UUID):
        try:
            self.logger.info(f"Attempting to log out user: {user_id}")
            stmt = select(User).filter(User.id == user_id)
            result = await self.db.execute(stmt)
            user_model = result.scalars().first()

            if user_model and user_model.is_active:
                user_model.is_active = False
                self.logger.info(f"User successfully logged out: {user_id}")
            else:
                self.logger.warning(
                    f"Logout attempted for inactive or non-existent user: {user_id}"
                )

        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error during user logout: {str(e)}",
                extra={"user_id": str(user_id), "error_type": type(e).__name__},
            )
            raise AuthenticationException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred when accessing the database!",
            )
