import json
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import Depends, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from pydantic import EmailStr
from jose import jwt
from config.auth_config import SECRET_KEY, ALGORITHM, oauth2_bearer

from config.parser import load_config
import random
import logging

logging.basicConfig(level=logging.INFO)


async def get_session() -> AsyncSession:
    raise NotImplementedError("Please overwrite get_session dependency.")


def db_model_to_dict(model_instance) -> dict:
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


def dict_to_db_model(model_class, data: dict):
    instance = model_class()
    for key, value in data.items():
        setattr(instance, key, value)
    return instance


async def get_current_user(user_token: str = Depends(oauth2_bearer)) -> dict:
    try:
        payload = jwt.decode(user_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("email")
        user_id: UUID = payload.get("id")

        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        else:
            return {"email": email, "id": user_id}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
