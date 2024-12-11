import json
import uuid
import pytest
from services.user_service import UserService
from exceptions.user_exceptions import UserException
from helper import add_test_users, get_test_users
import logging
from fastapi import status
from dependencies import db_model_to_dict
from models.models import User
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_get_all_users_success(test_session):
    """Test retrieving all users from the database"""
    user_service = UserService(test_session)

    test_users = get_test_users()
    await add_test_users(test_session, test_users)

    users = await user_service.get_all_users()

    actual_users = [
        {key: user[key] for key in user} for user in users
    ]
    expected_users = [db_model_to_dict(user) for user in test_users]

    assert len(users) == len(expected_users)
    assert sorted(actual_users, key=lambda x: x["email"]) == sorted(expected_users, key=lambda x: x["email"])


@pytest.mark.asyncio
async def test_get_all_users_no_users(test_session):
    """Test retrieving all users when there are no users in the database"""
    user_service = UserService(test_session)

    users = await user_service.get_all_users()

    assert users == []


@pytest.mark.asyncio
async def test_get_user_by_id(test_session):
    """Test retrieving all users from the database"""
    user_service = UserService(test_session)

    test_users = get_test_users()
    await add_test_users(test_session, test_users)

    actual_user = await user_service.get_user_by_id(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791"))

    expected_user = db_model_to_dict(test_users[0])

    assert actual_user == expected_user


@pytest.mark.asyncio
async def test_get_user_by_id_user_not_found(test_session):
    """Test retrieving a user by ID when the user does not exist in the database"""
    user_service = UserService(test_session)
    non_existing_user_id = uuid.uuid4()

    with pytest.raises(UserException) as exc_info:
        await user_service.get_user_by_id(non_existing_user_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == f"User with id {non_existing_user_id} not found!"


@pytest.mark.asyncio
async def test_get_users_by_role_positive(test_session):
    """Test retrieving users by role (is_seller)"""
    user_service = UserService(test_session)

    test_users = get_test_users()
    await add_test_users(test_session, test_users)

    # Test for sellers
    sellers = await user_service.get_users_by_role(is_seller=True)
    # Assuming only 1 seller in the test data
    assert len(sellers) == 1
    assert sellers[0]["email"] == "seller@example.com"
    assert sellers[0]["is_seller"] is True

    # Test for non-sellers
    non_sellers = await user_service.get_users_by_role(is_seller=False)
    # Assuming only 1 non-seller in the test data
    assert len(non_sellers) == 1
    assert non_sellers[0]["email"] == "buyer@example.com"
    assert non_sellers[0]["is_seller"] is False


@pytest.mark.asyncio
async def test_get_users_by_role_negative(test_session):
    """Test retrieving users by role (is_seller) when no users exist"""
    user_service = UserService(test_session)

    # Test for sellers with no seller users
    sellers = await user_service.get_users_by_role(is_seller=True)
    assert sellers == []

    # Test for non-sellers with no non-seller users
    non_sellers = await user_service.get_users_by_role(is_seller=False)
    assert non_sellers == []


@pytest.mark.asyncio
async def test_get_user_by_email_positive(test_session):
    """Test retrieving a user by email"""
    user_service = UserService(test_session)

    test_user = get_test_users()[0]
    await add_test_users(test_session, [test_user])

    actual_user = await user_service.get_user_by_email("seller@example.com")
    assert actual_user == test_user


@pytest.mark.asyncio
async def test_get_user_by_email_negative(test_session):
    """Test retrieving a user by email when the user does not exist"""
    user_service = UserService(test_session)

    # Test retrieving a user by a non-existing email
    with pytest.raises(UserException) as exc_info:
        await user_service.get_user_by_email("nonexistent@example.com")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No user found with email nonexistent@example.com"


@pytest.mark.asyncio
async def test_check_seller_exists_positive(test_session):
    """Test checking if a seller exists"""
    user_service = UserService(test_session)

    test_user = get_test_users()[0]
    await add_test_users(test_session, [test_user])

    seller_exists = await user_service.check_seller_exists(test_user.id)
    assert seller_exists is True


@pytest.mark.asyncio
async def test_create_new_user_positive(test_session):
    """Test checking if a seller exists"""
    user_service = UserService(test_session)

    test_user = get_test_users()[0]

    response = await user_service.create_new_user(test_user)
    assert isinstance(response, JSONResponse)

    response_json = json.loads(response.body.decode())

    assert response.status_code == status.HTTP_201_CREATED
    assert "message" in response_json
    assert response_json["message"] == "User created successfully"
    assert "user_id" in response_json
    assert isinstance(response_json["user_id"], str)
    assert response_json["user_id"] == str(test_user.id)

    saved_user = await test_session.get(User, test_user.id)
    assert saved_user is not None
    assert saved_user.id == test_user.id
