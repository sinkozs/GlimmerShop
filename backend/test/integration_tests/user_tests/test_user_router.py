import pytest
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from unittest.mock import AsyncMock
import logging

from exceptions.user_exceptions import UserException
from schemas.response_schemas import UserResponse

logger = logging.getLogger(__name__)


# pytestmark = pytest.mark.asyncio

class TestUserRoutes:
    @pytest.fixture
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
                "last_login": "2024-12-17T05:50:55"
            },
            {
                "id": "123e4567-e89b-12d3-a456-426614174789",
                "first_name": "John",
                "last_name": "Test",
                "email": "john@example.com",
                "is_seller": True,
                "is_verified": True,
                "is_active": False,
                "last_login": "2024-12-14T08:50:55"
            },
            {
                "id": "888e4567-e89b-12d3-a456-426614175555",
                "email": "buyer@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "is_seller": False,
                "is_verified": False,
                "is_active": False,
            }

        ]

    class TestGetAllUsers:
        @pytest.mark.asyncio
        async def test_get_all_users_success(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock,
                test_users: list
        ):
            """Test successful GET /users request"""
            mock_user_controller.get_all_users.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "users": test_users
                }
            )
            response = await async_test_client.get("/users")
            assert response.status_code == status.HTTP_200_OK
            assert "users" in response.json()
            assert len(response.json()["users"]) > 0
            mock_user_controller.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_empty(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock
        ):
            """Test GET /users when no users exist"""
            mock_user_controller.get_all_users.return_value = {"users": []}
            response = await async_test_client.get("/users")

            assert response.status_code == status.HTTP_200_OK
            assert "users" in response.json()
            assert len(response.json()["users"]) == 0
            mock_user_controller.get_all_users.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_all_users_error(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock,
                test_users: list
        ):
            """Test GET /users when an error occurs"""
            mock_user_controller.get_all_users.return_value = {
                "users": test_users
            }
            mock_user_controller.get_all_users.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
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
                test_users: list
        ):
            """Test successful GET /users/{user_id} request"""
            test_user_id = test_users[0]["id"]
            mock_user_controller.get_user_by_id.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"user": test_users[0]}
            )

            response = await async_test_client.get(f"/users/{test_user_id}")

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert "user" in response_json
            assert response_json["user"] == test_users[0]
            mock_user_controller.get_user_by_id.assert_awaited_once_with(test_user_id)

        @pytest.mark.asyncio
        async def test_get_user_by_id_not_found(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock
        ):
            """Test GET /users/{user_id} with non-existent user"""
            non_existent_id = "non-existent-id"
            mock_user_controller.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            response = await async_test_client.get(f"/users/{non_existent_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "User not found"
            mock_user_controller.get_user_by_id.assert_awaited_once_with(non_existent_id)

        @pytest.mark.asyncio
        async def test_get_user_by_id_error(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock,
                test_users: list
        ):
            """Test GET /users/{user_id} when an error occurs"""
            mock_user_controller.get_user_by_id.return_value = {
                "user": test_users[0]
            }
            mock_user_controller.get_user_by_id.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
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
                test_users: list
        ):
            """Test GET /users/by-type for sellers"""
            seller_users = [user for user in test_users if user["is_seller"]]
            mock_user_controller.get_users_by_type.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "users": seller_users,
                    "user_type": True
                }
            )

            response = await async_test_client.get("/users/by-type", params={"is_seller": True})

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert "users" in response_json
            assert response_json["users"] == seller_users
            assert "user_type" in response_json
            assert response_json["user_type"] is True

            mock_user_controller.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_buyers(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock,
                test_users: list
        ):
            """Test GET /users/by-type for buyers"""
            buyer_users = [user for user in test_users if not user["is_seller"]]
            mock_user_controller.get_users_by_type.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "users": buyer_users,
                    "user_type": False
                }
            )

            response = await async_test_client.get("/users/by-type", params={"is_seller": False})

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert "users" in response_json
            assert response_json["users"] == buyer_users
            assert "user_type" in response_json
            assert response_json["user_type"] is False

            mock_user_controller.get_users_by_type.assert_awaited_once()

        @pytest.mark.asyncio
        async def test_get_users_by_type_missing_param(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock
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
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock
        ):
            """Test GET /users/by-type with invalid is_seller parameter"""
            response = await async_test_client.get("/users/by-type", params={"is_seller": "not-a-boolean"})

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
                test_users: list
        ):
            """Test successful seller search"""

            search_query = "john"
            mock_sellers = [user for user in test_users if user["is_seller"]]
            mock_user_controller.search_sellers.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "sellers": mock_sellers
                }
            )
            response = await async_test_client.get("/users/sellers/search", params={"query": search_query})

            assert response.status_code == status.HTTP_200_OK
            assert "sellers" in response.json()
            sellers_list = response.json()["sellers"]
            assert len(sellers_list) == 2
            assert all(seller["is_seller"] for seller in sellers_list)
            assert all(search_query.lower() in seller["first_name"].lower() for seller in sellers_list)
            mock_user_controller.search_sellers.assert_awaited_once_with(search_query)

        @pytest.mark.asyncio
        async def test_search_sellers_no_results(
                self,
                async_test_client: AsyncClient,
                mock_user_controller: AsyncMock,
        ):
            """Test seller search with no matching results"""
            search_query = "nonexistent"
            mock_user_controller.search_sellers.return_value = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "sellers": []
                }
            )
            response = await async_test_client.get("/users/sellers/search", params={"query": search_query})

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["sellers"] == []
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
                error["msg"] == "Field required"
                and error["loc"] == ["query", "query"]
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
                detail="Search query cannot be empty or whitespace only"
            )

            response = await async_test_client.get("/users/sellers/search", params={"query": "  "})

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
            search_query = "test"
            mock_user_controller.search_sellers.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

            response = await async_test_client.get("/users/sellers/search", params={"query": search_query})

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Database error occurred"
            mock_user_controller.search_sellers.assert_awaited_once_with(search_query)
