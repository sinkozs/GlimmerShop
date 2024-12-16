import uuid
from unittest.mock import AsyncMock

import pytest
from datetime import datetime, date, timezone
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status

from dependencies import verify_code, hash_password
from schemas.schemas import UserCreate
from services.user_service import UserService
from exceptions.user_exceptions import UserException
from test.integration_tests.user_tests.helper import add_test_users, assert_user_dicts, assert_user_field_types
from models.models import User, Cart


class TestUserService:
    @pytest.fixture
    def test_users(self) -> list[dict]:
        # Test user data to directly insert to the DB
        return [
            {
                "id": uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791"),
                "first_name": "John",
                "last_name": "Doe",
                "email": "seller@example.com",
                "hashed_password": hash_password("strongpassword"),
                "is_seller": True,
                "is_verified": True,
                "is_active": True,
                "last_login": datetime.now(),
                "registration_date": date.today(),
                "password_length": 14
            },
            {
                "id": uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb792"),
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "buyer@example.com",
                "hashed_password": hash_password("securepassword"),
                "is_seller": False,
                "is_verified": False,
                "is_active": False,
                "last_login": None,
                "registration_date": date.today(),
                "password_length": 13
            }
        ]

    @pytest.fixture
    def test_users_pydantic_model(self) -> list[UserCreate]:
        return [
            UserCreate(
                first_name="John",
                last_name="Doe",
                email="seller@example.com",
                password="strongpassword",
                is_seller=True
            ),
            UserCreate(
                first_name="Jane",
                last_name="Smith",
                email="buyer@example.com",
                password="securepassword",
                is_seller=False
            )
        ]

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
            assert exc_info.value.detail == f"User with id {non_existing_user_id} not found"

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

    class TestGetUsersByType:
        @pytest.mark.asyncio
        async def test_get_users_by_type_returns_correct_users(self, test_users, test_session):
            """Test retrieving users by role (is_seller)"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            # Test for sellers
            sellers = await user_service.get_users_by_type(is_seller=True)
            # Assuming only 1 seller in the test data
            assert len(sellers) == 1
            assert sellers[0]["email"] == "seller@example.com"
            assert sellers[0]["is_seller"] is True

            # Test for non-sellers
            non_sellers = await user_service.get_users_by_type(is_seller=False)
            # Assuming only 1 non-seller in the test data
            assert len(non_sellers) == 1
            assert non_sellers[0]["email"] == "buyer@example.com"
            assert non_sellers[0]["is_seller"] is False

        @pytest.mark.asyncio
        async def test_get_users_by_type_correct_data_format(self, test_users, test_session):
            """Test that returned data has correct format and types"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            sellers = await user_service.get_users_by_type(is_seller=True)

            assert isinstance(sellers, list)
            if sellers:
                first_seller = sellers[0]
                assert first_seller["is_seller"] is True
                assert_user_field_types(first_seller)

        @pytest.mark.asyncio
        async def test_get_users_by_type_no_users_exist(self, test_session):
            """Test getting users by role when database is empty"""
            user_service = UserService(test_session)

            # Verify database is actually empty
            async with test_session.begin():
                result = await test_session.execute(select(User))
                assert result.scalars().all() == [], "Database should be empty"

            sellers = await user_service.get_users_by_type(is_seller=True)
            assert sellers == []
            assert isinstance(sellers, list)

            non_sellers = await user_service.get_users_by_type(is_seller=False)
            assert non_sellers == []
            assert isinstance(non_sellers, list)

        @pytest.mark.asyncio
        async def test_get_users_by_type_database_error(self, test_session, mocker):
            """Test database error handling"""
            user_service = UserService(test_session)

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.get_users_by_type(is_seller=True)

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
            assert exc_info.value.detail == "User with email nonexistent@example.com not found"

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
        async def test_check_seller_exists_not_found(self, test_users, test_session):
            """Test checking if the service raises UserException for a non-seller"""
            user_service = UserService(test_session)
            await add_test_users(test_session, test_users)

            # test_users[1] is a non-seller
            with pytest.raises(UserException) as exc_info:
                await user_service.check_seller_exists(test_users[1]["id"])

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == f"Seller with ID {test_users[1]['id']} not found"

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
            assert message == "Account successfully verified"

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

        @pytest.mark.asyncio
        async def test_update_is_verified_success(self, test_users, test_session):
            """Test successful update of is_verified column"""
            await add_test_users(test_session, test_users)
            test_email = test_users[1]["email"]

            user_service = UserService(test_session)
            result = await user_service.update_is_verified_column(test_email)

            assert isinstance(result, dict)
            assert result["email"] == test_email
            assert result["is_verified"] is True
            assert "id" in result

            # Verify database was actually updated
            async with test_session.begin():
                stmt = select(User).filter(User.email == test_email)
                db_user = (await test_session.execute(stmt)).scalars().first()
                assert db_user.is_verified is True

        @pytest.mark.asyncio
        async def test_update_is_verified_user_not_found(self, test_session):
            """Test updating verification status for non-existent user"""
            user_service = UserService(test_session)
            nonexistent_email = "nonexistent@example.com"

            with pytest.raises(UserException) as exc:
                await user_service.update_is_verified_column(nonexistent_email)

            assert exc.value.status_code == status.HTTP_404_NOT_FOUND
            assert f"User with email {nonexistent_email} not found" in str(exc.value.detail)

        @pytest.mark.asyncio
        async def test_update_is_verified_database_error(self, test_session, mocker):
            """Test handling of database errors during update"""
            user_service = UserService(test_session)
            test_email = "test@example.com"

            # Mock database error
            mocker.patch.object(
                test_session,
                'execute',
                side_effect=SQLAlchemyError("Test database error")
            )

            with pytest.raises(UserException) as exc:
                await user_service.update_is_verified_column(test_email)

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

        @pytest.mark.asyncio
        async def test_update_is_verified_returns_correct_types(self, test_users, test_session):
            """Test that returned data has correct types and format"""
            await add_test_users(test_session, test_users)
            test_email = test_users[0]["email"]

            user_service = UserService(test_session)
            result = await user_service.update_is_verified_column(test_email)

            assert isinstance(result, dict)
            assert isinstance(result["id"], str)
            assert isinstance(result["email"], str)
            assert isinstance(result["is_verified"], bool)
            assert str(test_users[0]["id"]) == result["id"]

    class TestCreateNewUser:
        @pytest.mark.asyncio
        async def test_create_seller_success(self, test_session, monkeypatch):
            """Test successful seller user creation"""
            # Mock send_verification_email
            mock_send_email = AsyncMock()
            monkeypatch.setattr('services.user_service.send_verification_email', mock_send_email)

            # Test data
            user_data = UserCreate(
                first_name="John",
                last_name="Doe",
                email="seller@example.com",
                password="StrongPass123!",
                is_seller=True
            )

            user_service = UserService(test_session)
            user_id = await user_service.create_new_user(user_data)

            # Verify user was created
            assert isinstance(user_id, str)

            # Verify user in database
            async with test_session.begin():
                stmt = select(User).filter(User.email == user_data.email)
                db_user = (await test_session.execute(stmt)).scalars().first()

                assert db_user is not None
                assert db_user.first_name == user_data.first_name
                assert db_user.last_name == user_data.last_name
                assert db_user.email == user_data.email
                assert db_user.is_seller is True
                assert db_user.cart is None  # Sellers don't get a cart
                assert db_user.password_length == len(user_data.password)

                # Verify password was hashed
                assert db_user.hashed_password != user_data.password
                assert len(db_user.hashed_password) > 0

            # Verify verification email was sent
            mock_send_email.assert_called_once_with(user_data.first_name, user_data.email)

        @pytest.mark.asyncio
        async def test_create_buyer_success(self, test_session, monkeypatch):
            """Test successful buyer user creation with cart"""
            # Mock send_verification_email
            mock_send_email = AsyncMock()
            monkeypatch.setattr('services.user_service.send_verification_email', mock_send_email)

            user_data = UserCreate(
                first_name="Jane",
                last_name="Smith",
                email="buyer@example.com",
                password="StrongPass456!",
                is_seller=False
            )

            user_service = UserService(test_session)
            user_id = await user_service.create_new_user(user_data)

            # Verify user and cart in database
            async with test_session.begin():
                stmt = select(User).filter(User.email == user_data.email)
                db_user = (await test_session.execute(stmt)).scalars().first()

                assert db_user is not None
                assert db_user.is_seller is False
                assert db_user.cart is not None
                assert isinstance(db_user.cart, Cart)

        @pytest.mark.asyncio
        async def test_create_user_database_error(self, test_session, mocker):
            """Test database error handling during user creation"""
            # Mock database error
            mocker.patch.object(
                test_session,
                'flush',
                side_effect=SQLAlchemyError("Test database error")
            )

            user_data = UserCreate(
                first_name="Error",
                last_name="Test",
                email="error@test.com",
                password="TestPass123!",
                is_seller=False
            )

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.create_new_user(user_data)

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "creating the user" in str(exc.value.detail)

        @pytest.mark.asyncio
        async def test_create_user_verification_email_error(self, test_session, monkeypatch):
            """Test handling of email sending failure"""

            # Mock email sending error
            async def mock_send_email(*args):
                raise Exception("Email sending failed")

            monkeypatch.setattr('services.user_service.send_verification_email', mock_send_email)

            user_data = UserCreate(
                first_name="Test",
                last_name="Email",
                email="test@email.com",
                password="TestPass789!",
                is_seller=False
            )

            user_service = UserService(test_session)

            # User should still be created even if email fails
            user_id = await user_service.create_new_user(user_data)

            assert isinstance(user_id, str)

            # Verify user was created in database
            async with test_session.begin():
                stmt = select(User).filter(User.email == user_data.email)
                db_user = (await test_session.execute(stmt)).scalars().first()
                assert db_user is not None

        @pytest.mark.asyncio
        async def test_password_hashing(self, test_session, monkeypatch):
            """Test that password is properly hashed"""
            # Mock email sending
            monkeypatch.setattr('services.user_service.send_verification_email', AsyncMock())

            user_data = UserCreate(
                first_name="Pass",
                last_name="Test",
                email="pass@test.com",
                password="SuperSecret123!",
                is_seller=False
            )

            user_service = UserService(test_session)
            await user_service.create_new_user(user_data)

            # Verify password was hashed
            async with test_session.begin():
                stmt = select(User).filter(User.email == user_data.email)
                db_user = (await test_session.execute(stmt)).scalars().first()

                assert db_user.hashed_password != user_data.password
                assert len(db_user.hashed_password) > 0
                assert db_user.password_length == len(user_data.password)

        @pytest.mark.asyncio
        async def test_registration_date(self, test_session, monkeypatch):
            """Test that registration date is set correctly"""
            monkeypatch.setattr('services.user_service.send_verification_email', AsyncMock())

            user_data = UserCreate(
                first_name="Date",
                last_name="Test",
                email="date@test.com",
                password="DatePass123!",
                is_seller=False
            )

            user_service = UserService(test_session)
            await user_service.create_new_user(user_data)

            today = datetime.now(timezone.utc).date()

            async with test_session.begin():
                stmt = select(User).filter(User.email == user_data.email)
                db_user = (await test_session.execute(stmt)).scalars().first()

                assert db_user.registration_date == today

    class TestEditUser:
        @pytest.mark.asyncio
        async def test_edit_user_success(self, test_users, test_session):
            """Test successful user update"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]

            update_data = {
                "first_name": "UpdatedName",
                "last_name": "UpdatedLast",
                "email": "updated@example.com"
            }

            user_service = UserService(test_session)
            result = await user_service.edit_user(user_id, update_data)

            assert result["first_name"] == update_data["first_name"]
            assert result["last_name"] == update_data["last_name"]
            assert result["email"] == update_data["email"]

            # Verify database was updated
            async with test_session.begin():
                stmt = select(User).filter(User.id == user_id)
                db_user = (await test_session.execute(stmt)).scalars().first()
                assert db_user.first_name == update_data["first_name"]
                assert db_user.last_name == update_data["last_name"]
                assert db_user.email == update_data["email"]

        @pytest.mark.asyncio
        async def test_edit_user_not_found(self, test_session):
            """Test updating non-existent user"""
            non_existent_id = uuid.uuid4()
            update_data = {"first_name": "Test"}

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.edit_user(non_existent_id, update_data)

            assert exc.value.status_code == status.HTTP_404_NOT_FOUND
            assert f"User with id {non_existent_id} not found" in str(exc.value.detail)

        @pytest.mark.asyncio
        async def test_edit_user_partial_update(self, test_users, test_session):
            """Test partial update with only some fields"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]
            original_last_name = test_users[0]["last_name"]

            update_data = {
                "first_name": "UpdatedFirstOnly"
            }

            user_service = UserService(test_session)
            result = await user_service.edit_user(user_id, update_data)

            # Verify only specified field was updated
            assert result["first_name"] == update_data["first_name"]
            assert result["last_name"] == original_last_name  # Unchanged

            # Verify in database
            async with test_session.begin():
                stmt = select(User).filter(User.id == user_id)
                db_user = (await test_session.execute(stmt)).scalars().first()
                assert db_user.first_name == update_data["first_name"]
                assert db_user.last_name == original_last_name

        @pytest.mark.asyncio
        async def test_edit_user_database_error(self, test_users, test_session, mocker):
            """Test handling of database errors"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]

            # Mock database error
            mocker.patch.object(
                test_session,
                'flush',
                side_effect=SQLAlchemyError("Test database error")
            )

            update_data = {"first_name": "ShouldFail"}

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.edit_user(user_id, update_data)

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

        @pytest.mark.asyncio
        async def test_edit_user_empty_update(self, test_users, test_session):
            """Test update with empty update data"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]
            original_data = test_users[0].copy()

            update_data = {}

            user_service = UserService(test_session)
            result = await user_service.edit_user(user_id, update_data)

            # Verify no changes
            assert result["first_name"] == original_data["first_name"]
            assert result["last_name"] == original_data["last_name"]
            assert result["email"] == original_data["email"]

        @pytest.mark.asyncio
        async def test_edit_user_invalid_field(self, test_users, test_session):
            """Test update with invalid field name"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]

            update_data = {
                "invalid_field": "some_value"  # Field that doesn't exist in User model
            }

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.edit_user(user_id, update_data)

            assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid fields" in str(exc.value.detail)

        @pytest.mark.asyncio
        async def test_edit_user_preserve_other_fields(self, test_users, test_session):
            """Test that non-updated fields preserve their values"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]
            original_data = test_users[0].copy()

            update_data = {
                "first_name": "UpdatedName"
            }

            user_service = UserService(test_session)
            result = await user_service.edit_user(user_id, update_data)

            # Verify updated field
            assert result["first_name"] == update_data["first_name"]

            # Verify other fields remained unchanged
            assert result["last_name"] == original_data["last_name"]
            assert result["email"] == original_data["email"]
            assert result["is_seller"] == original_data["is_seller"]
            assert result["is_verified"] == original_data["is_verified"]

    class TestDeleteUser:
        @pytest.mark.asyncio
        async def test_delete_user_success(self, test_users, test_session):
            """Test successful user deletion"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]

            user_service = UserService(test_session)
            result = await user_service.delete_user(user_id)

            assert isinstance(result, dict)
            assert "message" in result
            assert "user_id" in result
            assert result["user_id"] == str(user_id)
            assert result["message"] == "User deleted successfully"

            async with test_session.begin():
                stmt = select(User).filter(User.id == user_id)
                db_user = (await test_session.execute(stmt)).scalars().first()
                assert db_user is None

        @pytest.mark.asyncio
        async def test_delete_user_not_found(self, test_session):
            """Test deleting non-existent user"""
            non_existent_id = uuid.uuid4()

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.delete_user(non_existent_id)

            assert exc.value.status_code == status.HTTP_404_NOT_FOUND
            assert f"User with id {non_existent_id} not found" in str(exc.value.detail)

        @pytest.mark.asyncio
        async def test_delete_user_database_error(self, test_users, test_session, mocker):
            """Test handling of database errors during deletion"""
            await add_test_users(test_session, test_users)
            user_id = test_users[0]["id"]

            # Mock database error
            mocker.patch.object(
                test_session,
                'delete',
                side_effect=SQLAlchemyError("Test database error")
            )

            user_service = UserService(test_session)

            with pytest.raises(UserException) as exc:
                await user_service.delete_user(user_id)

            assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "database" in str(exc.value.detail).lower()

        @pytest.mark.asyncio
        async def test_delete_user_cascading(self, test_users, test_session):
            """Test that related records are deleted properly"""
            buyer_data = test_users[1]

            async with test_session.begin():
                user = User(**buyer_data)
                user.cart = Cart(user=user)
                test_session.add(user)

            user_service = UserService(test_session)
            result = await user_service.delete_user(buyer_data["id"])

            assert result["user_id"] == str(buyer_data["id"])

            # Verify cart was also deleted (cascade)
            async with test_session.begin():
                cart_stmt = select(Cart).filter(Cart.user_id == buyer_data["id"])
                cart = (await test_session.execute(cart_stmt)).scalars().first()
                assert cart is None

                # Verify user was deleted
                user_stmt = select(User).filter(User.id == buyer_data["id"])
                user = (await test_session.execute(user_stmt)).scalars().first()
                assert user is None

        @pytest.mark.asyncio
        async def test_delete_multiple_users(self, test_users, test_session):
            """Test deleting multiple users sequentially"""
            await add_test_users(test_session, test_users)

            user_service = UserService(test_session)

            # Delete users one by one
            for test_user in test_users:
                user_id = test_user["id"]
                result = await user_service.delete_user(user_id)
                assert result["user_id"] == str(user_id)

                async with test_session.begin():
                    stmt = select(User).filter(User.id == user_id)
                    db_user = (await test_session.execute(stmt)).scalars().first()
                    assert db_user is None

            # Verify all users are deleted
            async with test_session.begin():
                stmt = select(User)
                remaining_users = (await test_session.execute(stmt)).scalars().all()
                assert len(remaining_users) == 0
