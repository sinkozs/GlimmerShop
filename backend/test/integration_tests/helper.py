import uuid
from datetime import date, datetime
from typing import Union, List

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import dict_to_db_model
from models.models import User
import pytest


async def add_test_users(session: AsyncSession, test_users) -> None:
    test_user_models = [dict_to_db_model(User, user) for user in test_users]
    for user in test_user_models:
        session.add(user)
    await session.commit()


def get_required_user_fields():
    return {
        "id",
        "email",
        "first_name",
        "last_name",
        "is_seller",
        "is_verified",
        "is_active",
        "registration_date",
        "last_login"
    }


def get_test_user_service_response() -> list[dict]:
    return [
        {
            "id": str(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791")),
            "first_name": "John",
            "last_name": "Doe",
            "email": "seller@example.com",
            "is_seller": True,
            "is_verified": True,
            "is_active": True,
            "last_login": datetime.now().isoformat(),
        },
        {
            "id": str(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb792")),
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "buyer@example.com",
            "is_seller": False,
            "is_verified": False,
            "is_active": False,
            "last_login": None,
        }
    ]


def assert_user_dicts(
        expected: Union[dict, List[dict]],
        actual: Union[dict, List[dict]]
):
    """
    Compare user dictionaries for equality of important fields.
    Accepts either single dict or list of dicts.

    Args:
        expected: Expected user data (dict or list of dicts)
        actual: Actual user data (dict or list of dicts)
    """
    # Convert single dicts to lists
    expected_users = [expected] if isinstance(expected, dict) else expected
    actual_users = [actual] if isinstance(actual, dict) else actual

    assert len(actual_users) == len(expected_users), "Lists have different lengths"

    # Only sort if we have multiple users
    if len(expected_users) > 1:
        expected_users = sorted(expected_users, key=lambda x: x["email"])
        actual_users = sorted(actual_users, key=lambda x: x["email"])

    for actual, expected in zip(actual_users, expected_users):
        # Required fields
        assert actual["id"] == expected["id"], f"ID mismatch: {actual['id']} != {expected['id']}"
        assert actual["first_name"] == expected["first_name"], f"First name mismatch"
        assert actual["last_name"] == expected["last_name"], f"Last name mismatch"
        assert actual["email"] == expected["email"], f"Email mismatch: {actual['email']} != {expected['email']}"

        assert actual["is_seller"] == expected["is_seller"], f"Seller status mismatch"
        assert actual["is_verified"] == expected["is_verified"], f"User verification mismatch"

        # Optional fields
        if expected["last_login"] is not None:
            assert isinstance(actual["last_login"], str), "Last login should be string"
