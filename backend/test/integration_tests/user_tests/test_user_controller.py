import json

import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from schemas.schemas import UserUpdate
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
    def sample_user(self):
        return {
            "id": "dce380e7-6191-40aa-ac73-63fb372841fa",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "hashed_password": "$2b$12$8EXg7kqAZnwgx8DP.sdrburMSH0Y/4aU5rSXX/7c0xrr9BBnRFTN2",
            "is_seller": False,
            "is_verified": False,
            "is_active": True,
            "last_login": None
        }

    @pytest.fixture
    def user_update(self):
        return UserUpdate(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="newpassword123"
        )

    @pytest.fixture
    def edited_user(self):
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

    class TestEditUser:
        # bcrypt generates a different hash each time, even for the same password, because it uses a random salt.
        # Therefore, we don't perform an assertion on the hashed_password field.
        @pytest.mark.asyncio
        async def test_edit_user_successful_update(
                self, controller, mock_service, sample_user, user_update, edited_user
        ):
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
            assert "user" in response_content

            expected_response = UserResponse.model_validate(edited_user).model_dump()
            assert response_content["user"] == expected_response

            mock_service.get_user_by_id.assert_awaited_once_with(user_id)

        @pytest.mark.asyncio
        async def test_edit_user_no_changes(
                self, controller, mock_service, sample_user, user_update
        ):
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
                self, controller, mock_service, sample_user, user_update
        ):
            user_id = sample_user["id"]
            mock_service.get_user_by_id.side_effect = UserException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await controller.edit_user(user_id, user_update)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert str(exc_info.value.detail) == "User not found"
            mock_service.edit_user.assert_not_awaited()
