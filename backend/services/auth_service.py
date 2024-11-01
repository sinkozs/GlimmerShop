from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from pydantic import EmailStr
from fastapi import status, Response
from fastapi.responses import JSONResponse
from jose import jwt
import secrets
import string
from datetime import datetime, timedelta
from uuid import UUID

from models.models import User
from config.auth_config import bcrypt_context, encryption_algorithm, http_only_auth_cookie
from exceptions.auth_exceptions import AuthenticationException
from dependencies import db_model_to_dict, send_password_reset_email, hash_password
from config.parser import load_config


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

    def create_access_token(self, user_id: UUID, email: EmailStr) -> str:
        encode = {"id": str(user_id), "email": str(email)}
        expire = datetime.now() + timedelta(minutes=self.auth_config.token_expiry_minutes)
        encode.update({"exp": expire})
        return jwt.encode(encode, self.auth_config.secret_key, algorithm=encryption_algorithm)

    async def set_response_cookie(self, user_id: UUID, email: EmailStr, response: Response):
        access_token = self.create_access_token(user_id=user_id, email=email)
        sign_in_response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(
            key=http_only_auth_cookie,
            value=access_token,
            httponly=True,
            max_age=3600,
            expires=3600,
            samesite="lax",
            secure=False
        )
        return sign_in_response

    async def authenticate_user(self, email: EmailStr, password: str) -> dict:
        async with self.db.begin():
            stmt = select(User).filter((User.email == email) & (User.is_seller == False))
            result = await self.db.execute(stmt)
            user_model = result.scalars().first()
            if user_model:
                user_dict = db_model_to_dict(user_model)

            if not user_model:
                raise AuthenticationException(detail="User not found!")
            if not self.verify_password(password, user_model.hashed_password):
                raise AuthenticationException(detail="Invalid credentials!")

            user_model.is_active = True
            user_model.last_login = datetime.now()
            self.db.add(user_model)
            await self.db.commit()
            return user_dict

    async def authenticate_seller(self, email: EmailStr, password: str) -> dict:
        try:
            async with self.db.begin():
                stmt = select(User).filter((User.email == email) & (User.is_seller == True))
                result = await self.db.execute(stmt)
                seller_model = result.scalars().first()
                if seller_model:
                    seller_dict = db_model_to_dict(seller_model)

                if not seller_model:
                    raise AuthenticationException(detail="Seller not found!")
                if not self.verify_password(password, seller_model.hashed_password):
                    raise AuthenticationException(detail="Invalid credentials!")

                seller_model.is_active = True
                seller_model.last_login = datetime.now()
                self.db.add(seller_model)
                await self.db.commit()
                return seller_dict
        except SQLAlchemyError:
            raise AuthenticationException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                          detail="An error occurred when accessing the database!")

    async def regenerate_forgotten_password(self, email: EmailStr):
        try:
            async with self.db.begin():
                stmt = select(User).filter(User.email == email)
                result = await self.db.execute(stmt)
                user_model = result.scalars().first()
                if user_model:
                    new_password = self.generate_strong_password()
                    user_model.hashed_password = hash_password(new_password)
                    self.db.add(user_model)
                    await self.db.commit()
                    await send_password_reset_email(email, new_password)
                if not user_model:
                    raise AuthenticationException()
        except SQLAlchemyError:
            raise AuthenticationException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                          detail="An error occurred when accessing the database!")

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
