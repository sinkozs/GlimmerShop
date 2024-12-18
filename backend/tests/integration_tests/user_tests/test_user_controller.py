import json
import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from schemas.schemas import UserUpdate, UserCreate, UserVerification
from schemas.response_schemas import UserResponse
from controllers.user_controller import UserController
from exceptions.user_exceptions import UserException


class TestUserController:
    @pytest.fixture
    def mock_service(self):
        service = AsyncMock()
        service.get_user_by_id = AsyncMock()
        service.edit_user = AsyncMock()
        service.delete_user = AsyncMock()
        return service

    @pytest.fixture
    def controller(self, mock_service):
        return UserController(user_service=mock_service)

    @pytest.fixture
    def mock_user_id(self):
        return UUID("123e4567-e89b-12d3-a456-426614174000")

    @pytest.fixture
    def sample_users(self) -> list[dict]:
        return [{
            "id": "dce380e7-6191-40aa-ac73-63fb372841fa",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "hashed_password": "$2b$12$8EXg7kqAZnwgx8DP.sdrburMSH0Y/4aU5rSXX/7c0xrr9BBnRFTN2",
            "is_seller": False,
            "is_verified": False,
            "is_active": True,
            "last_login": None
        },

            {
                "id": "dce380e7-6191-40aa-ac73-63fb372841fb",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "hashed_password": "$2b$12$8EXg7kqAZnwgx8DP.sdrburMSH0Y/4aU5rSXX/7c0xrr9BBnRFTN2",
                "is_seller": True,
                "is_verified": True,
                "is_active": True,
                "last_login": None
            }]

    @pytest.fixture
    def user_update(self) -> UserUpdate:
        return UserUpdate(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="newpassword123"
        )

    @pytest.fixture
    def edited_user(self) -> dict:
        return {
            "id": "dce380e7-6191-40aa-ac73-63fb372841fa",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "hashed_password": "$2b$12$8EXg7kqAZnwgx8DP.sdrburMSH0Y/4aU5rSXX/7c0xrr9BBnRFNEW",
            "password_length": 12,
            "is_seller": True,
            "is_verified": False,
            "is_active": False,
            "last_login": None,
            "registration_date": "2024-12-16"
        }

    class TestGetUserById:
        @pytest.mark.asyncio
        async def test_get_user_by_id_success(
                self, controller, mock_service, sample_users
        ):
            sample_user = sample_users[0]
            user_id = sample_user["id"]
            mock_service.get_user_by_id.return_value = sample_user

            response = await controller.get_user_by_id(user_id)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 1
            assert "user" in response_content

            expected_response = UserResponse.model_validate(sample_user).model_dump()
            assert response_content["user"] == expected_response

            mock_service.get_user_by_id.assert_awaited_once_with(user_id=user_id)

        @pytest.mark.asyncio
        async def test_get_user_by_id_not_found(
                self, controller, mock_service, mock_user_id
        ):
            mock_service.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.get_user_by_id(mock_user_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "User not found"

            mock_service.get_user_by_id.assert_awaited_once_with(user_id=mock_user_id)

        @pytest.mark.asyncio
        async def test_get_user_by_id_server_error(
                self, controller, mock_service
        ):
            user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_service.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.get_user_by_id(user_id)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.get_user_by_id.assert_awaited_once_with(user_id=user_id)

    class TestGetAllUsers:
        @pytest.mark.asyncio
        async def test_get_all_users_success(
                self, controller, mock_service, sample_users
        ):
            mock_service.get_all_users.return_value = sample_users

            response = await controller.get_all_users()

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 1
            assert "users" in response_content
            assert isinstance(response_content["users"], list)
            assert len(response_content["users"]) == 2

            expected_users = [
                UserResponse.model_validate(user).model_dump()
                for user in sample_users
            ]
            assert response_content["users"] == expected_users

            mock_service.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_empty_list(
                self, controller, mock_service
        ):
            mock_service.get_all_users.return_value = []

            response = await controller.get_all_users()

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 1

            assert "users" in response_content
            assert isinstance(response_content["users"], list)
            assert len(response_content["users"]) == 0

            mock_service.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_server_error(
                self, controller, mock_service
        ):
            mock_service.get_all_users.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.get_all_users()

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.get_all_users.assert_awaited_once()

    class TestGetUsersByType:

        @pytest.mark.asyncio
        async def test_get_users_by_type_success(self, controller, mock_service, sample_users):
            is_seller = True
            test_seller = sample_users[1]
            mock_service.get_users_by_type.return_value = [test_seller]
            response = await controller.get_users_by_type(is_seller=is_seller)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            expected_user = UserResponse.model_validate(test_seller).model_dump()
            assert len(response_content) == 2

            assert "users" in response_content
            assert len(response_content["users"]) > 0
            assert isinstance(response_content["users"], list)
            assert response_content["users"][0] == expected_user
            assert isinstance(response_content["users"][0], dict)

            assert "user_type" in response_content
            assert isinstance(response_content["user_type"], bool)
            assert response_content["user_type"] == is_seller

            mock_service.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_empty_list(
                self, controller, mock_service
        ):
            is_seller = True
            mock_service.get_users_by_type.return_value = []

            response = await controller.get_users_by_type(is_seller=is_seller)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 2

            assert "users" in response_content
            assert isinstance(response_content["users"], list)
            assert len(response_content["users"]) == 0

            assert "user_type" in response_content
            assert isinstance(response_content["user_type"], bool)
            assert response_content["user_type"] == is_seller

            mock_service.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_server_error(
                self, controller, mock_service
        ):
            mock_service.get_users_by_type.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.get_users_by_type()

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.get_users_by_type.assert_awaited_once()

    class TestGetUserByEmail:
        @pytest.mark.asyncio
        async def test_get_user_by_email_success(self, controller, mock_service, sample_users):
            test_seller = sample_users[0]
            mock_service.get_user_by_email.return_value = test_seller
            response = await controller.get_user_by_email(email=test_seller["email"])

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            expected_user = UserResponse.model_validate(test_seller).model_dump()
            assert len(response_content) == 1

            assert "user" in response_content
            assert isinstance(response_content["user"], dict)
            assert len(response_content["user"]) > 0
            assert response_content["user"] == expected_user

            mock_service.get_user_by_email.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_user_by_email_user_not_found(self, controller, mock_service):
            test_email = "john@example.com"
            mock_service.get_user_by_email.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {test_email} not found"
            )
            with pytest.raises(HTTPException) as exc_info:
                await controller.get_user_by_email(test_email)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == f"User with email {test_email} not found"

            mock_service.get_user_by_email.assert_awaited_once_with(test_email)

        @pytest.mark.asyncio
        async def test_get_user_by_email_server_error(
                self, controller, mock_service
        ):
            mock_service.get_user_by_email.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.get_user_by_email("john@example.com")

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.get_user_by_email.assert_awaited_once()

    class TestCheckSellerExists:
        @pytest.mark.asyncio
        async def test_check_seller_exists_success(self, controller, mock_service, mock_user_id):
            mock_service.check_seller_exists.return_value = True
            response = await controller.check_seller_exists(seller_id=mock_user_id)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 2

            assert "seller_id" in response_content
            assert isinstance(response_content["seller_id"], str)
            assert response_content["seller_id"] == str(mock_user_id)

            assert "exists" in response_content
            assert isinstance(response_content["exists"], bool)
            assert response_content["exists"] is True

            mock_service.check_seller_exists.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_check_seller_exists_seller_not_found(self, controller, mock_service, mock_user_id):
            mock_service.check_seller_exists.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Seller with ID {mock_user_id} not found"
            )
            with pytest.raises(HTTPException) as exc_info:
                await controller.check_seller_exists(mock_user_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == f"Seller with ID {mock_user_id} not found"

            mock_service.check_seller_exists.assert_awaited_once_with(mock_user_id)

        @pytest.mark.asyncio
        async def test_check_seller_exists_server_error(
                self, controller, mock_service, mock_user_id
        ):
            mock_service.check_seller_exists.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )
            with pytest.raises(HTTPException) as exc_info:
                await controller.check_seller_exists(mock_user_id)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.check_seller_exists.assert_awaited_once()

    class TestSearchSellers:
        @pytest.mark.asyncio
        async def test_search_sellers_success(self, controller, mock_service, sample_users):
            # sample_users[1] is a seller
            search_query = "jane"
            test_sellers = [sample_users[1]]
            mock_service.search_sellers.return_value = test_sellers

            response = await controller.search_sellers(query=search_query)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert "sellers" in response_content
            assert isinstance(response_content["sellers"], list)
            assert len(response_content["sellers"]) == 1

            seller_data = response_content["sellers"][0]
            expected_seller = UserResponse.model_validate(test_sellers[0]).model_dump()
            assert seller_data == expected_seller

            mock_service.search_sellers.assert_awaited_once_with(search_query)

        @pytest.mark.asyncio
        async def test_search_sellers_empty_results(self, controller, mock_service):
            search_query = "nonexistent"
            mock_service.search_sellers.return_value = []

            response = await controller.search_sellers(query=search_query)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert "sellers" in response_content
            assert isinstance(response_content["sellers"], list)
            assert len(response_content["sellers"]) == 0

            mock_service.search_sellers.assert_awaited_once_with(search_query)

        @pytest.mark.asyncio
        async def test_search_sellers_error(self, controller, mock_service):
            search_query = "tests"
            mock_service.search_sellers.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.search_sellers(query=search_query)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert str(exc_info.value.detail) == "Database error occurred"

            mock_service.search_sellers.assert_awaited_once_with(search_query)

    class TestCreateNewUser:
        @pytest.mark.asyncio
        async def test_create_new_user_success(self, controller, mock_service):
            user_data = UserCreate(
                email="tests@example.com",
                password="Password123!",
                first_name="Test",
                last_name="User",
                is_seller=False
            )
            test_user_id = "123e4567-e89b-12d3-a456-426614174000"
            mock_service.create_new_user.return_value = test_user_id

            response = await controller.create_new_user(user_data)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_201_CREATED

            response_content = json.loads(response.body.decode('utf-8'))
            assert "userId" in response_content
            assert response_content["userId"] == test_user_id

            mock_service.create_new_user.assert_awaited_once_with(user_data)

        @pytest.mark.asyncio
        async def test_create_new_user_duplicate_email(self, controller, mock_service):
            user_data = UserCreate(
                email="existing@example.com",
                password="Password123!",
                first_name="Test",
                last_name="User",
                is_seller=False
            )
            mock_service.create_new_user.side_effect = UserException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.create_new_user(user_data)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert str(exc_info.value.detail) == "User with this email already exists"

            mock_service.create_new_user.assert_awaited_once_with(user_data)

        @pytest.mark.asyncio
        async def test_create_new_user_server_error(self, controller, mock_service):
            user_data = UserCreate(
                email="tests@example.com",
                password="Password123!",
                first_name="Test",
                last_name="User",
                is_seller=False
            )
            mock_service.create_new_user.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.create_new_user(user_data)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert str(exc_info.value.detail) == "Database error occurred"

            mock_service.create_new_user.assert_awaited_once_with(user_data)

    class TestVerifyUser:
        @pytest.mark.asyncio
        async def test_verify_user_success(self, controller, mock_service):
            verification = UserVerification(
                email="tests@example.com",
                code="123456"
            )
            mock_service.verify_email.return_value = None

            response = await controller.verify_user(verification)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert "message" in response_content
            assert "email" in response_content
            assert response_content["message"] == "User verified successfully"
            assert response_content["email"] == verification.email

            mock_service.verify_email.assert_awaited_once_with(
                verification.email,
                verification.code
            )

        @pytest.mark.asyncio
        async def test_verify_user_invalid_code(self, controller, mock_service):
            verification = UserVerification(
                email="tests@example.com",
                code="invalid"
            )
            mock_service.verify_email.side_effect = UserException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.verify_user(verification)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert str(exc_info.value.detail) == "Invalid verification code"

            mock_service.verify_email.assert_awaited_once_with(
                verification.email,
                verification.code
            )

        @pytest.mark.asyncio
        async def test_verify_user_user_not_found(self, controller, mock_service):
            verification = UserVerification(
                email="nonexistent@example.com",
                code="123456"
            )
            mock_service.verify_email.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.verify_user(verification)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == "User not found"

            mock_service.verify_email.assert_awaited_once_with(
                verification.email,
                verification.code
            )

        @pytest.mark.asyncio
        async def test_verify_user_already_verified(self, controller, mock_service):
            verification = UserVerification(
                email="verified@example.com",
                code="123456"
            )
            mock_service.verify_email.side_effect = UserException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already verified"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.verify_user(verification)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert str(exc_info.value.detail) == "User is already verified"

            mock_service.verify_email.assert_awaited_once_with(
                verification.email,
                verification.code
            )

    class TestResendVerificationEmail:
        @pytest.mark.asyncio
        async def test_resend_verification_email_success(
                self, controller, mock_service, mocker, sample_users
        ):
            test_user = sample_users[0]
            test_user_email = sample_users[0]["email"]
            mock_service.get_user_by_email.return_value = test_user

            mock_send_email = mocker.patch(
                "dependencies.send_verification_email",
                return_value=True
            )

            response = await controller.resend_verification_email(test_user_email)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert "message" in response_content
            assert response_content["message"] == "Verification email sent successfully"

            mock_service.get_user_by_email.assert_awaited_once_with(test_user_email)
            mock_send_email.assert_awaited_once_with(
                test_user["first_name"],
                test_user["email"]
            )

        @pytest.mark.asyncio
        async def test_resend_verification_email_user_not_found(
                self, controller, mock_service
        ):
            test_email = "nonexistent@example.com"
            mock_service.get_user_by_email.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await controller.resend_verification_email(test_email)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == "User not found"

            mock_service.get_user_by_email.assert_awaited_once_with(test_email)

        @pytest.mark.asyncio
        async def test_resend_verification_email_already_verified(
                self, controller, mock_service
        ):
            test_email = "verified@example.com"
            test_user = {
                "email": test_email,
                "first_name": "Test",
                "is_verified": True
            }
            mock_service.get_user_by_email.return_value = test_user

            with pytest.raises(HTTPException) as exc_info:
                await controller.resend_verification_email(test_email)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert str(exc_info.value.detail) == "User account is already verified!"

            mock_service.get_user_by_email.assert_awaited_once_with(test_email)

        @pytest.mark.asyncio
        async def test_resend_verification_email_send_failure(
                self, controller, mock_service, mocker
        ):
            test_email = "tests@example.com"
            test_user = {
                "email": test_email,
                "first_name": "Test",
                "is_verified": False
            }
            mock_service.get_user_by_email.return_value = test_user

            mock_send_email = mocker.patch(
                "dependencies.send_verification_email",
                return_value=False
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.resend_verification_email(test_email)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert str(exc_info.value.detail) == "Failed to send verification email"

            mock_service.get_user_by_email.assert_awaited_once_with(test_email)
            mock_send_email.assert_called_once_with(
                test_user["first_name"],
                test_user["email"]
            )

        @pytest.mark.asyncio
        async def test_resend_verification_email_service_error(
                self, controller, mock_service
        ):
            test_email = "tests@example.com"
            mock_service.get_user_by_email.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.resend_verification_email(test_email)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert str(exc_info.value.detail) == "Database error occurred"

            mock_service.get_user_by_email.assert_awaited_once_with(test_email)

    class TestEditUser:
        # bcrypt generates a different hash each time, even for the same password, because it uses a random salt.
        # Therefore, we don't perform an assertion on the hashed_password field.
        @pytest.mark.asyncio
        async def test_edit_user_successful_update(
                self, controller, mock_service, sample_users, user_update, edited_user
        ):
            sample_user = sample_users[0]
            user_id = sample_user["id"]
            mock_service.get_user_by_id.return_value = sample_user

            with patch('dependencies.is_valid_update', return_value=True), \
                    patch('config.auth_config.bcrypt_context.verify', return_value=False), \
                    patch('dependencies.hash_password',
                          return_value="$2b$12$8EXg7kqAZnwgx8DP.sdrburMSH0Y/4aU5rSXX/7c0xrr9BBnRFNEW"):
                mock_service.edit_user.return_value = edited_user
                response = await controller.edit_user(user_id, user_update)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert len(response_content) == 1
            assert "user" in response_content

            expected_response = UserResponse.model_validate(edited_user).model_dump()
            assert response_content["user"] == expected_response

            mock_service.get_user_by_id.assert_awaited_once_with(user_id)
            mock_service.edit_user.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_edit_user_no_changes(
                self, controller, mock_service, sample_users
        ):
            sample_user = sample_users[0]
            user_id = sample_user["id"]
            mock_service.get_user_by_id.return_value = sample_user

            no_change_update = UserUpdate(
                first_name=sample_user["first_name"],
                last_name=sample_user["last_name"],
                email=sample_user["email"],
                password=None
            )

            with patch('dependencies.is_valid_update', return_value=False), \
                    patch('config.auth_config.bcrypt_context.verify', return_value=True):
                response = await controller.edit_user(user_id, no_change_update)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_304_NOT_MODIFIED

            response_content = json.loads(response.body.decode('utf-8'))
            assert "user" in response_content

            expected_response = UserResponse.model_validate(sample_user).model_dump()
            assert response_content["user"] == expected_response

            mock_service.get_user_by_id.assert_awaited_once_with(user_id)
            mock_service.edit_user.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_edit_user_not_found(
                self, controller, mock_service, sample_users, user_update
        ):
            user_id = sample_users[0]["id"]
            mock_service.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.edit_user(user_id, user_update)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == "User not found"
            mock_service.edit_user.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_edit_user_server_error(
                self, controller, mock_service, sample_users, user_update
        ):
            sample_user = sample_users[0]
            user_id = sample_user["id"]
            mock_service.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.edit_user(user_id, user_update)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Database connection error"

            mock_service.get_user_by_id.assert_awaited_once_with(user_id)
            mock_service.edit_user.assert_not_awaited()

    class TestDeleteUser:
        @pytest.mark.asyncio
        async def test_delete_user_success(self, controller, mock_service):
            test_user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_service.delete_user.return_value = {
                "message": "User deleted successfully",
                "user_id": str(test_user_id)
            }

            response = await controller.delete_user(test_user_id)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK

            response_content = json.loads(response.body.decode('utf-8'))
            assert "user_id" in response_content
            assert response_content["user_id"] == str(test_user_id)

            mock_service.delete_user.assert_awaited_once_with(test_user_id)

        @pytest.mark.asyncio
        async def test_delete_user_not_found(self, controller, mock_service):
            test_user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_service.delete_user.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {test_user_id} not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.delete_user(test_user_id)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == f"User with id {test_user_id} not found"

            mock_service.delete_user.assert_awaited_once_with(test_user_id)

        @pytest.mark.asyncio
        async def test_delete_user_database_error(self, controller, mock_service):
            test_user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
            mock_service.delete_user.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting user"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.delete_user(test_user_id)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert str(exc_info.value.detail) == "Database error occurred while deleting user"

            mock_service.delete_user.assert_awaited_once_with(test_user_id)
