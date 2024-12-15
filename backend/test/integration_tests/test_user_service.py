import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status

from config.parser import load_config
from dependencies import smtp_config, verify_code
from services.user_service import UserService
from exceptions.user_exceptions import UserException
from helper import add_test_users, get_required_user_fields, assert_user_dicts, assert_user_field_types
from models.models import User


class TestUserService:
    class TestGetAllUsers:
        @pytest.mark.asyncio
        async def test_get_all_users_success(self, test_users: list[dict], test_session):
            """Test retrieving all users from the database"""
            user_service = UserService(test_session)

            await add_test_users(test_session, test_users)

            users = await user_service.get_all_users()

            assert_user_dicts(test_users, users)

        @pytest.mark.asyncio
        async def test_get_all_users_correct_data_types(self, test_users, test_session):
            """Test that returned user data contains all required fields and correct data types"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            users = await user_service.get_all_users()

            assert isinstance(users, list)
            assert isinstance(users[0], dict)
            [assert_user_field_types(u) for u in users]

        @pytest.mark.asyncio
        async def test_get_all_users_no_users(self, test_session):
            """Test retrieving all users when there are no users in the database"""
            # Setup
            user_service = UserService(test_session)

            # Verify database is empty first
            async with test_session.begin():
                result = await test_session.execute(select(User))
                assert result.scalars().all() == [], "Database should be empty"

            users = await user_service.get_all_users()

            assert users == []
            assert isinstance(users, list)
            assert len(users) == 0

        @pytest.mark.asyncio
        async def test_get_all_users_database_error(self, test_session, mocker):
            """Test database error handling when retrieving users"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.get_all_users()

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in exc.value.detail.lower()

    class TestGetUserById:
        @pytest.mark.asyncio
        async def test_get_user_by_id_success(self, test_users, test_session):
            """Test retrieving a user by ID"""
            user_service = UserService(test_session)

            await add_test_users(test_session, test_users)

            actual_user = await user_service.get_user_by_id(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791"))

            assert_user_dicts(test_users[0], actual_user)

        @pytest.mark.asyncio
        async def test_get_user_by_id_user_not_found(self, test_session):
            """Test retrieving a user by ID when the user does not exist in the database"""
            user_service = UserService(test_session)
            non_existing_user_id = uuid.uuid4()

            with pytest.raises(UserException) as exc_info:
                await user_service.get_user_by_id(non_existing_user_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == f"User with id {non_existing_user_id} not found!"

        @pytest.mark.asyncio
        async def test_get_user_by_id_database_error(self, test_session, mocker):
            """Test database error handling when retrieving user by id"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.get_user_by_id(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791"))

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in exc.value.detail.lower()

    class TestGetUsersByRole:
        @pytest.mark.asyncio
        async def test_get_users_by_role_returns_correct_users(self, test_users, test_session):
            """Test retrieving users by role (is_seller)"""
            user_service = UserService(test_session)
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
        async def test_get_users_by_role_correct_data_format(self, test_users, test_session):
            """Test that returned data has correct format and types"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            sellers = await user_service.get_users_by_role(is_seller=True)

            assert isinstance(sellers, list)
            if sellers:
                first_seller = sellers[0]
                assert first_seller["is_seller"] is True
                assert_user_field_types(first_seller)

        @pytest.mark.asyncio
        async def test_get_users_by_role_no_users_exist(self, test_session):
            """Test getting users by role when database is empty"""
            user_service = UserService(test_session)

            # Verify database is actually empty
            async with test_session.begin():
                result = await test_session.execute(select(User))
                assert result.scalars().all() == [], "Database should be empty"

            sellers = await user_service.get_users_by_role(is_seller=True)
            assert sellers == []
            assert isinstance(sellers, list)

            non_sellers = await user_service.get_users_by_role(is_seller=False)
            assert non_sellers == []
            assert isinstance(non_sellers, list)

        @pytest.mark.asyncio
        async def test_get_users_by_role_database_error(self, test_session, mocker):
            """Test database error handling"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.get_users_by_role(is_seller=True)

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

    class TestGetUserByEmail:
        @pytest.mark.asyncio
        async def test_get_user_by_email_success(self, test_users, test_session):
            """Test retrieving a user by email"""
            user_service = UserService(test_session)

            await add_test_users(test_session, test_users)

            actual_user = await user_service.get_user_by_email(email="seller@example.com")
            assert_user_dicts(test_users[0], actual_user)

        @pytest.mark.asyncio
        async def test_get_user_by_email_correct_data_format(self, test_users, test_session):
            """Test that returned data has correct format and types"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            actual_user = await user_service.get_user_by_email(email="seller@example.com")

            assert isinstance(actual_user, dict)
            assert_user_field_types(actual_user)

        @pytest.mark.asyncio
        async def test_get_user_by_email_negative(self, test_session):
            """Test retrieving a user by email when the user does not exist"""
            user_service = UserService(test_session)

            # Test retrieving a user by a non-existing email
            with pytest.raises(UserException) as exc_info:
                await user_service.get_user_by_email(email="nonexistent@example.com")

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "User with email nonexistent@example.com not found!"

        @pytest.mark.asyncio
        async def test_get_user_by_email_database_error(self, test_session, mocker):
            """Test database error handling"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.get_user_by_email(email="seller@example.com")

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

    class TestCheckSellerExists:
        @pytest.mark.asyncio
        async def test_check_seller_exists_true(self, test_users, test_session):
            """Test checking if a seller exists"""
            user_service = UserService(test_session)

            await add_test_users(test_session, test_users)

            # test_users[0] is a seller
            seller_exists = await user_service.check_seller_exists(test_users[0]["id"])
            assert seller_exists is True

        @pytest.mark.asyncio
        async def test_check_seller_exists_false(self, test_users, test_session):
            """Test checking if the service returns False for a non-seller """
            user_service = UserService(test_session)

            await add_test_users(test_session, test_users)

            # test_users[1] is a non-seller
            seller_exists = await user_service.check_seller_exists(test_users[1]["id"])
            assert seller_exists is False

        @pytest.mark.asyncio
        async def test_check_seller_exists_database_error(self, test_users, test_session, mocker):
            """Test database error handling"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.check_seller_exists(seller_id=test_users[0]["id"])

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

    class TestEmailVerification:
        @pytest.mark.asyncio
        async def test_verify_code_success(self, mock_verification_storage):
            """Test successful email verification"""
            email = "seller@example.com"
            code = "123456"

            is_verified, message = await verify_code(email, code, mock_verification_storage)

            assert is_verified is True
            assert message == "Account successfully verified!"

        @pytest.mark.asyncio
        async def test_verify_code_non_existing_email(self, mock_verification_storage):
            """Test email verification with invalid email"""
            email = "non-existing@example.com"
            code = "123456"

            is_verified, message = await verify_code(email, code, mock_verification_storage)

            assert is_verified is False
            assert message == "Invalid email or verification code"

        @pytest.mark.asyncio
        async def test_verify_code_invalid_code(self, mock_verification_storage):
            """Test email verification with invalid code"""
            email = "seller@example.com"
            code = "555555"

            is_verified, message = await verify_code(email, code, mock_verification_storage)

            assert is_verified is False
            assert message == "Invalid verification code"

        @pytest.mark.asyncio
        async def test_verify_code_expired_code(self, mock_verification_storage):
            """Test email verification with expired code"""
            email = "buyer@example.com"
            code = "222222"

            is_verified, message = await verify_code(email, code, mock_verification_storage)

            assert is_verified is False
            assert message == "Verification code expired"
