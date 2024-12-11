# helpers.py
import uuid
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User
from dependencies import hash_password


def get_test_users() -> list:
    users = [
        User(
            id=uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791"),
            first_name="John",
            last_name="Doe",
            email="seller@example.com",
            hashed_password=hash_password("strongpassword"),
            password_length=14,
            is_seller=True,
            is_verified=True,
            is_active=True,
            last_login=datetime.now(),
            registration_date=date.today(),
        ),
        User(
            id=uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb792"),
            first_name="Jane",
            last_name="Smith",
            email="buyer@example.com",
            hashed_password=hash_password("securepassword"),
            password_length=13,
            is_seller=False,
            is_verified=False,
            is_active=False,
            last_login=None,
            registration_date=date.today(),
        ),
    ]
    return users


async def add_test_users(session: AsyncSession, users_list: list[User]) -> None:
    for user in users_list:
        session.add(user)
    await session.commit()

