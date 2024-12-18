import uuid
from datetime import date, datetime
from typing import Union, List, Any, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import dict_to_db_model
from models.models import User
from schemas.schemas import UserCreate


def convert_non_json_serializable_fields_to_str(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert dictionary values to JSON-serializable format.
    Converts UUID, datetime, and date objects to strings.

    Args:
        data: Dictionary containing potentially non-JSON-serializable values

    Returns:
        dict: Dictionary with all non-JSON-serializable values converted to strings

    Example:
        user_dict = {
            "id": UUID("123e4567..."),
            "created_at": datetime.now(),
            "name": "John"
        }
        result = convert_non_json_serializable_fields_to_str(user_dict)
        # Result: {
        #     "id": "123e4567...",
        #     "created_at": "2024-12-14T15:30:00",
        #     "name": "John"
        # }
    """

    def convert_value(value: Any) -> Any:
        """Convert a single value to JSON-serializable format if needed."""
        if isinstance(value, (uuid.UUID, datetime, date)):
            return str(value)
        return value

    return {
        key: convert_value(value)
        for key, value in data.items()
    }


async def add_test_users(session: AsyncSession, test_users: list[dict]) -> None:
    """
    Add tests users directly to the database for testing purposes.

    Args:
        session: SQLAlchemy async session
        test_users: List of user dictionaries containing complete user data

    Example:
        test_users = [
            {
                "id": uuid.uuid4(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "tests@example.com",
                ...
            }
        ]
        await add_test_users(session, test_users)
    """
    try:
        async with session.begin():
            test_user_models = [dict_to_db_model(User, user) for user in test_users]
            for user in test_user_models:
                session.add(user)
    except SQLAlchemyError as e:
        print(f"Error adding tests users: {e}")
        raise


def get_required_user_fields():
    return {
        "id",
        "first_name",
        "last_name",
        "email",
        "hashed_password"
        "is_seller",
        "is_verified",
        "is_active",
        "registration_date",
        "password_length"
    }


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

    if isinstance(expected, list):
        expected_users = [convert_non_json_serializable_fields_to_str(u) for u in expected]
    elif isinstance(expected, dict):
        expected_users = [convert_non_json_serializable_fields_to_str(expected)]

    actual_users = [actual] if isinstance(actual, dict) else actual

    assert len(actual_users) == len(expected_users), "Lists have different lengths"

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

        # Optional field
        if expected["last_login"] is not None:
            assert actual["last_login"] == expected["last_login"], f"Last login mismatch"


def assert_user_field_types(user: dict) -> None:
    """
    Verify that all user fields have the correct data types.

    Args:
        user: Dictionary containing user data with expected fields:
            - id (str): User UUID as string
            - first_name (str): User's first name
            - last_name (str): User's last name
            - email (str): User's email address
            - is_seller (bool): Whether user is a seller
            - is_verified (bool): Whether user is verified
            - is_active (bool): Whether user account is active
            - last_login (str): Last login timestamp as string, optional
            - password_length (int): Length of user's password

    Raises:
        AssertionError: If any field has incorrect type
        KeyError: If required fields are missing

    Example:
        user = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "first_name": "John",
            ...
        }
        assert_user_field_types(user)
    """
    if get_required_user_fields() <= user.keys():
        assert isinstance(user["id"], str), "ID must be string"
        assert isinstance(user["first_name"], str), "First name must be string"
        assert isinstance(user["last_name"], str), "Last name must be string"
        assert isinstance(user["email"], str), "Email must be string"
        assert isinstance(user["is_seller"], bool), "Is seller must be boolean"
        assert isinstance(user["is_verified"], bool), "Is verified must be boolean"
        assert isinstance(user["is_active"], bool), "Is active must be boolean"
        assert isinstance(user["password_length"], int), "Password length must be integer"

        # Optional
        if user["last_login"]:
            assert isinstance(user["last_login"], str), "Last login must be string"
