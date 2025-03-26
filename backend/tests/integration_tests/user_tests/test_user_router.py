from uuid import UUID
import pytest
from fastapi import status, HTTPException
from httpx import AsyncClient
from unittest.mock import AsyncMock
import logging

from config.auth_config import http_only_auth_cookie
from exceptions.user_exceptions import UserException
from schemas.response_schemas import UserResponse
from schemas.schemas import UserCreate, UserVerification, UserUpdate

logger = logging.getLogger(__name__)


class TestUserRoutes:
    @pytest.fixture(scope="session")
    def test_users(self) -> list[dict]:
        return [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe",
                "email": "seller@example.com",
                "is_seller": True,
                "is_verified": True,
                "is_active": False,
                "last_login": "2024-12-17T05:50:55",
            },
            {
                "id": "123e4567-e89b-12d3-a456-426614174789",
                "first_name": "John",
                "last_name": "Test",
                "email": "john@example.com",
                "is_seller": True,
                "is_verified": True,
                "is_active": False,
                "last_login": "2024-12-14T08:50:55",
            },
            {
                "id": "888e4567-e89b-12d3-a456-426614175555",
                "email": "buyer@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "is_seller": False,
                "is_verified": False,
                "is_active": False,
            },
        ]

    class TestGetAllUsers:
        @pytest.mark.asyncio
        async def test_get_all_users_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            expected_response = [
                UserResponse.model_validate(user).model_dump() for user in test_users
            ]
            mock_user_controller.get_all_users.return_value = expected_response

            response = await async_test_client.get("/users")

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), list)
            assert response.json() == expected_response
            mock_user_controller.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_empty(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            """Test GET /users when no users exist"""
            mock_user_controller.get_all_users.return_value = []
            response = await async_test_client.get("/users")

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), list)
            assert len(response.json()) == 0
            mock_user_controller.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_error(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            """Test GET /users when an error occurs"""
            mock_user_controller.get_all_users.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )

            response = await async_test_client.get("/users")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "detail" in response.json()
            assert response.json()["detail"] == "Database error occurred"
            mock_user_controller.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_users_invalid_path(self, async_test_client: AsyncClient):
            """Test invalid path returns 404"""
            response = await async_test_client.get("/invalid")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "detail" in response.json()
            assert response.json()["detail"] == "Not Found"

    class TestGetUserById:
        @pytest.mark.asyncio
        async def test_get_user_by_id_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            """Test successful GET /users/{user_id} request"""
            test_user_id = test_users[0]["id"]
            mock_user_controller.get_user_by_id.return_value = (
                UserResponse.model_validate(test_users[0]).model_dump()
            )

            response = await async_test_client.get(f"/users/{test_user_id}")
            response_json = response.json()

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response_json, dict)
            assert response_json == test_users[0]
            mock_user_controller.get_user_by_id.assert_awaited_once_with(test_user_id)

        @pytest.mark.asyncio
        async def test_get_user_by_id_not_found(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            """Test GET /users/{user_id} with non-existent user"""
            non_existent_id = "non-existent-id"
            mock_user_controller.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

            response = await async_test_client.get(f"/users/{non_existent_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "User not found"
            mock_user_controller.get_user_by_id.assert_awaited_once_with(
                non_existent_id
            )

        @pytest.mark.asyncio
        async def test_get_user_by_id_error(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            """Test GET /users/{user_id} when an error occurs"""
            mock_user_controller.get_user_by_id.return_value = (
                UserResponse.model_validate(test_users[0]).model_dump()
            )
            mock_user_controller.get_user_by_id.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )

            response = await async_test_client.get(f"/users/{test_users[0]['id']}")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "detail" in response.json()
            assert response.json()["detail"] == "Database error occurred"
            mock_user_controller.get_user_by_id.assert_awaited_once()

    class TestGetUserByType:
        @pytest.mark.asyncio
        async def test_get_users_by_type_sellers(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            """Test GET /users/by-type for sellers"""
            sellers = [
                UserResponse.model_validate(user).model_dump()
                for user in test_users
                if user["is_seller"]
            ]
            mock_user_controller.get_users_by_type.return_value = sellers

            response = await async_test_client.get(
                "/users/by-type", params={"is_seller": True}
            )

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert isinstance(response_json, list)
            assert len(response_json) == len(sellers)

            assert isinstance(response_json[0], dict)
            assert response_json == sellers
            assert response_json[0]["is_seller"] is True

            mock_user_controller.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_buyers(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            """Test GET /users/by-type for buyers"""
            buyers = [
                UserResponse.model_validate(user).model_dump()
                for user in test_users
                if not user["is_seller"]
            ]
            mock_user_controller.get_users_by_type.return_value = buyers

            response = await async_test_client.get(
                "/users/by-type", params={"is_seller": False}
            )

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert isinstance(response_json, list)
            assert len(response_json) == len(buyers)

            assert isinstance(response_json[0], dict)
            assert response_json == buyers
            assert response_json[0]["is_seller"] is False

            mock_user_controller.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_missing_param(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            """Test GET /users/by-type with missing is_seller parameter"""
            response = await async_test_client.get("/users/by-type")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            error_detail = response.json()["detail"]
            assert any(
                error["msg"] == "Field required"
                and error["loc"] == ["query", "is_seller"]
                for error in error_detail
            )
            mock_user_controller.get_users_by_type.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_get_users_by_type_invalid_param(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            """Test GET /users/by-type with invalid is_seller parameter"""
            response = await async_test_client.get(
                "/users/by-type", params={"is_seller": "not-a-boolean"}
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            error_detail = response.json()["detail"]
            assert any(
                error["msg"].startswith("Input should be a valid boolean")
                and error["loc"] == ["query", "is_seller"]
                for error in error_detail
            )
            mock_user_controller.get_users_by_type.assert_not_awaited()

    class TestSellerSearchEndpoint:
        @pytest.mark.asyncio
        async def test_search_sellers_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_users: list,
        ):
            """Test successful seller search"""

            search_query = "john"
            mock_sellers = [
                UserResponse.model_validate(user).model_dump()
                for user in test_users
                if user["is_seller"]
            ]
            mock_user_controller.search_sellers.return_value = mock_sellers
            response = await async_test_client.get(
                "/users/sellers/search", params={"query": search_query}
            )

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()

            assert isinstance(response_json, list)
            assert len(response_json) == len(mock_sellers)

            assert len(response_json) == 2
            assert all(seller["is_seller"] for seller in response_json)
            assert all(
                search_query.lower() in seller["first_name"].lower()
                for seller in response_json
            )
            mock_user_controller.search_sellers.assert_awaited_once_with(search_query)

        @pytest.mark.asyncio
        async def test_search_sellers_no_results(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            """Test seller search with no matching results"""
            search_query = "nonexistent"
            mock_user_controller.search_sellers.return_value = []
            response = await async_test_client.get(
                "/users/sellers/search", params={"query": search_query}
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
            mock_user_controller.search_sellers.assert_awaited_once_with(search_query)

        @pytest.mark.asyncio
        async def test_search_sellers_missing_query(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            """Test seller search with missing query parameter"""
            response = await async_test_client.get("/users/sellers/search")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            error_detail = response.json()["detail"]
            assert any(
                error["msg"] == "Field required" and error["loc"] == ["query", "query"]
                for error in error_detail
            )
            mock_user_controller.search_sellers.assert_not_awaited()

        async def test_search_sellers_empty_query(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            """Test search sellers with empty query string"""
            mock_user_controller.search_sellers.side_effect = UserException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Search query cannot be empty or whitespace only",
            )

            response = await async_test_client.get(
                "/users/sellers/search", params={"query": "  "}
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            error_detail = response.json()["detail"]
            assert error_detail == "Search query cannot be empty or whitespace only"

            mock_user_controller.return_value.search_sellers.assert_not_awaited()

        @pytest.mark.asyncio
        async def test_search_sellers_service_error(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            """Test seller search when service raises an error"""
            search_query = "tests"
            mock_user_controller.search_sellers.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )

            response = await async_test_client.get(
                "/users/sellers/search", params={"query": search_query}
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Database error occurred"
            mock_user_controller.search_sellers.assert_awaited_once_with(search_query)

    class TestCreateNewUser:
        @pytest.fixture
        def test_new_user(self):
            return UserCreate(
                first_name="Anna",
                last_name="Test",
                email="tests@example.com",
                password="securepass123",
                is_seller=False,
            )

        @pytest.mark.asyncio
        async def test_create_new_user_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_new_user: UserCreate,
        ):
            expected_user_id = "123e4567-e89b-12d3-a456-426614174000"
            mock_user_controller.create_new_user.return_value = {
                "user_id": expected_user_id
            }

            response = await async_test_client.post(
                "/users", json=test_new_user.model_dump()
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {"user_id": expected_user_id}
            mock_user_controller.create_new_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_create_new_user_duplicate_email(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_new_user: UserCreate,
        ):
            error_message = "User with this email already exists"
            mock_user_controller.create_new_user.side_effect = UserException(
                status_code=status.HTTP_409_CONFLICT, detail=error_message
            )

            response = await async_test_client.post(
                "/users", json=test_new_user.model_dump()
            )

            assert response.status_code == status.HTTP_409_CONFLICT
            assert response.json() == {"detail": error_message}
            mock_user_controller.create_new_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_create_new_user_missing_required_fields(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            incomplete_user_data = {
                "email": "tests@example.com",
                "password": "securepass123",
            }

            response = await async_test_client.post("/users", json=incomplete_user_data)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            mock_user_controller.create_new_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_create_new_user_invalid_email_format(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_user_data = {
                "first_name": "Anna",
                "last_name": "Test",
                "email": "invalid-email",
                "password": "securepass123",
                "is_seller": False,
            }

            response = await async_test_client.post("/users", json=invalid_user_data)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            assert any("email" in error["loc"] for error in response.json()["detail"])
            mock_user_controller.create_new_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_create_new_user_password_too_short(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_user_data = {
                "first_name": "Anna",
                "last_name": "Test",
                "email": "tests@example.com",
                "password": "short",
                "is_seller": False,
            }

            response = await async_test_client.post("/users", json=invalid_user_data)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            assert any(
                "password" in error["loc"] for error in response.json()["detail"]
            )
            mock_user_controller.create_new_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_create_new_user_server_error(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_new_user: UserCreate,
        ):
            error_message = "Internal server error"
            mock_user_controller.create_new_user.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message
            )

            response = await async_test_client.post(
                "/users", json=test_new_user.model_dump()
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {"detail": error_message}
            mock_user_controller.create_new_user.assert_called_once()

    class TestVerifyUser:
        @pytest.fixture
        def test_verification_data(self) -> UserVerification:
            return UserVerification(email="tests@example.com", code="123456")

        @pytest.mark.asyncio
        async def test_verify_user_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_verification_data: UserVerification,
        ):
            mock_user_controller.verify_user.return_value = {"is_verified": True}

            response = await async_test_client.post(
                "/users/verification", json=test_verification_data.model_dump()
            )

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), dict)
            assert response.json()["is_verified"] is True
            mock_user_controller.verify_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_verify_user_invalid_code(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_verification_data: UserVerification,
        ):
            error_message = "Invalid verification code"
            mock_user_controller.verify_user.side_effect = UserException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

            response = await async_test_client.post(
                "/users/verification", json=test_verification_data.model_dump()
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": error_message}
            mock_user_controller.verify_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_verify_user_expired_code(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_verification_data: UserVerification,
        ):
            error_message = "Verification code has expired"
            mock_user_controller.verify_user.side_effect = UserException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

            response = await async_test_client.post(
                "/users/verification", json=test_verification_data.model_dump()
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": error_message}
            mock_user_controller.verify_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_verify_user_email_not_found(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_verification_data: UserVerification,
        ):
            error_message = "Email not found"
            mock_user_controller.verify_user.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message
            )

            response = await async_test_client.post(
                "/users/verification", json=test_verification_data.model_dump()
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": error_message}
            mock_user_controller.verify_user.assert_called_once()

        @pytest.mark.asyncio
        async def test_verify_user_invalid_email_format(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_data = {"email": "invalid-email", "code": "123456"}

            response = await async_test_client.post(
                "/users/verification", json=invalid_data
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            assert any("email" in error["loc"] for error in response.json()["detail"])
            mock_user_controller.verify_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_verify_user_missing_code(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_data = {"email": "tests@example.com"}

            response = await async_test_client.post(
                "/users/verification", json=invalid_data
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            assert any("code" in error["loc"] for error in response.json()["detail"])
            mock_user_controller.verify_user.assert_not_called()

    class TestResendVerification:
        @pytest.mark.asyncio
        async def test_resend_verification_success(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            test_email = "tests@example.com"
            mock_user_controller.resend_verification_email.return_value = {
                "email": test_email
            }

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": test_email}
            )
            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), dict)
            assert response.json()["email"] == test_email

            mock_user_controller.resend_verification_email.assert_called_once_with(
                test_email
            )

        @pytest.mark.asyncio
        async def test_resend_verification_user_not_found(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            test_email = "nonexistent@example.com"
            mock_user_controller.resend_verification_email.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": test_email}
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "User not found"}
            mock_user_controller.resend_verification_email.assert_called_once_with(
                test_email
            )

        @pytest.mark.asyncio
        async def test_resend_verification_already_verified(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            test_email = "verified@example.com"
            mock_user_controller.resend_verification_email.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is already verified!",
            )

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": test_email}
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": "User account is already verified!"}
            mock_user_controller.resend_verification_email.assert_called_once_with(
                test_email
            )

        @pytest.mark.asyncio
        async def test_resend_verification_email_sending_failed(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            test_email = "tests@example.com"
            mock_user_controller.resend_verification_email.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email",
            )

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": test_email}
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {"detail": "Failed to send verification email"}
            mock_user_controller.resend_verification_email.assert_called_once_with(
                test_email
            )

        @pytest.mark.asyncio
        async def test_resend_verification_invalid_email_format(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_email = "invalid-email"

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": invalid_email}
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            assert any("email" in error["loc"] for error in response.json()["detail"])
            mock_user_controller.resend_verification_email.assert_not_called()

        @pytest.mark.asyncio
        async def test_resend_verification_missing_email(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            response = await async_test_client.post("/users/verification/resend")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()
            mock_user_controller.resend_verification_email.assert_not_called()

        @pytest.mark.asyncio
        async def test_resend_verification_service_error(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            test_email = "tests@example.com"
            mock_user_controller.resend_verification_email.side_effect = UserException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal service error",
            )

            response = await async_test_client.post(
                "/users/verification/resend", params={"email": test_email}
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {"detail": "Internal service error"}
            mock_user_controller.resend_verification_email.assert_called_once_with(
                test_email
            )

    class TestEditUser:
        @pytest.fixture
        def update_data(self) -> UserUpdate:
            return UserUpdate(
                first_name="Johnny", last_name="Smith", email="johnny@example.com"
            )

        @pytest.mark.asyncio
        async def test_edit_user_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_user_id: str,
            auth_headers: dict,
            update_data: UserUpdate,
        ):
            updated_user = {
                "id": test_user_id,
                "first_name": "Johnny",
                "last_name": "Smith",
                "email": "johnny@example.com",
                "is_seller": False,
                "is_verified": True,
                "is_active": False,
                "last_login": None,
            }

            mock_user_controller.edit_user.return_value = UserResponse.model_validate(
                updated_user
            ).model_dump()

            response = await async_test_client.put(
                "/users/me",
                json=update_data.model_dump(exclude_unset=True),
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["first_name"] == update_data.first_name
            assert response_data["last_name"] == update_data.last_name
            assert response_data["email"] == update_data.email
            mock_user_controller.edit_user.assert_called_once_with(
                UUID(test_user_id), update_data
            )

    @pytest.mark.asyncio
    async def test_edit_user_no_token(
        self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
    ):
        update_data = UserUpdate(first_name="Johnny")

        response = await async_test_client.put(
            "/users/me", json=update_data.model_dump(exclude_unset=True)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
        mock_user_controller.edit_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_user_invalid_token(
        self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
    ):
        invalid_headers = {"cookie": f"{http_only_auth_cookie}=invalid_token"}
        update_data = UserUpdate(first_name="Johnny")

        response = await async_test_client.put(
            "/users/me",
            json=update_data.model_dump(exclude_unset=True),
            headers=invalid_headers,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
        mock_user_controller.edit_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_user_expired_token(
        self,
        async_test_client: AsyncClient,
        mock_user_controller: AsyncMock,
        test_user_id: UUID,
        test_user_email: str,
    ):
        expired_headers = {"cookie": f"{http_only_auth_cookie}=expired_token"}
        update_data = UserUpdate(first_name="Johnny")

        response = await async_test_client.put(
            "/users/me",
            json=update_data.model_dump(exclude_unset=True),
            headers=expired_headers,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
        mock_user_controller.edit_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_user_validation_error(
        self,
        async_test_client: AsyncClient,
        mock_user_controller: AsyncMock,
        auth_headers: dict,
    ):
        invalid_data = {"email": "invalid-email"}

        response = await async_test_client.put(
            "/users/me", json=invalid_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        assert any("email" in error["loc"] for error in response.json()["detail"])
        mock_user_controller.edit_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_user_no_changes(
        self,
        async_test_client: AsyncClient,
        mock_user_controller: AsyncMock,
        test_user_id: str,
        auth_headers: dict,
    ):
        current_user = {
            "id": test_user_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "is_seller": False,
            "is_verified": True,
            "is_active": False,
            "last_login": None,
        }
        update_data = UserUpdate(
            first_name="John", last_name="Doe", email="john@example.com"
        )
        expected_response = UserResponse.model_validate(current_user).model_dump()
        mock_user_controller.edit_user.return_value = expected_response

        response = await async_test_client.put(
            "/users/me",
            json=update_data.model_dump(exclude_unset=True),
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response
        mock_user_controller.edit_user.assert_called_once()

    class TestDeleteUser:
        @pytest.mark.asyncio
        async def test_delete_user_success(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
            test_user_id: str,
            auth_headers: dict,
        ):
            mock_user_controller.delete_user.return_value = {
                "user_id": str(test_user_id)
            }

            response = await async_test_client.delete("/users/me", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), dict)
            assert response.json()["user_id"] == test_user_id
            mock_user_controller.delete_user.assert_called_once_with(UUID(test_user_id))

        @pytest.mark.asyncio
        async def test_delete_user_no_token(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            response = await async_test_client.delete("/users/me")

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Not authenticated"
            mock_user_controller.delete_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_delete_user_invalid_token(
            self, async_test_client: AsyncClient, mock_user_controller: AsyncMock
        ):
            invalid_headers = {"cookie": f"{http_only_auth_cookie}=invalid_token"}

            response = await async_test_client.delete(
                "/users/me", headers=invalid_headers
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Not authenticated"
            mock_user_controller.delete_user.assert_not_called()

        @pytest.mark.asyncio
        async def test_delete_user_expired_token(
            self,
            async_test_client: AsyncClient,
            mock_user_controller: AsyncMock,
        ):
            expired_headers = {"cookie": f"{http_only_auth_cookie}=expired_token"}

            response = await async_test_client.delete(
                "/users/me", headers=expired_headers
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Not authenticated"
            mock_user_controller.delete_user.assert_not_called()
