from datetime import datetime, timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from typing import AsyncGenerator, Any
from config.auth_config import http_only_auth_cookie
from jose import jwt
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from models.database import Base, build_session_maker
from dependencies import get_session, get_current_user
from routers.user_router import get_user_controller, get_user_service
import logging
from dotenv import load_dotenv
import os
from unittest.mock import AsyncMock

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_user_id() -> str:
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture(scope="session")
def test_user_email() -> str:
    return "tests@example.com"


@pytest.fixture(scope="session")
def test_auth_token(test_user_id: str, test_user_email: str) -> str:
    payload = {
        "id": str(test_user_id),
        "email": test_user_email,
        "exp": datetime.now() + timedelta(minutes=15)
    }
    return jwt.encode(
        payload,
        "<tests-secret-key>",
        algorithm="HS256"
    )


@pytest.fixture(scope="session")
def auth_headers(test_auth_token: str) -> dict:
    """Create headers with authentication cookie"""
    return {"cookie": f"{http_only_auth_cookie}={test_auth_token}"}


# Module scope - database setup and expensive operations shared within a test file
@pytest.fixture(scope="module")
def test_db_url():
    load_dotenv(".env.test")
    test_db_config = {
        "username": os.getenv("TEST_POSTGRES_USER"),
        "password": os.getenv("TEST_POSTGRES_PASSWORD"),
        "host": os.getenv("TEST_POSTGRES_HOST"),
        "port": int(os.getenv("TEST_POSTGRES_PORT", "5432")),
        "database": os.getenv("TEST_POSTGRES_DB"),
    }
    assert all(test_db_config.values()), "Missing test database environment variables!"

    return (
        f"postgresql+asyncpg://{test_db_config['username']}:{test_db_config['password']}"
        f"@{test_db_config['host']}:{test_db_config['port']}/{test_db_config['database']}"
    )


@pytest.fixture(scope="module")
def setup_test_env(test_db_url):
    os.environ["TEST_DATABASE_URL"] = test_db_url
    return test_db_url


@pytest_asyncio.fixture(scope="module")
async def test_engine(setup_test_env):
    engine = create_async_engine(os.getenv("TEST_DATABASE_URL"), echo=True)
    try:
        async with engine.begin() as conn:
            logger.info("Creating test database schema...")
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        async with engine.begin() as conn:
            logger.info("Dropping test database schema...")
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


# Function scope - fresh instances for each test
@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = build_session_maker(test_engine)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def mock_user_service():
    service = AsyncMock()
    return service


@pytest_asyncio.fixture
async def mock_user_controller():
    controller = AsyncMock()
    controller.configure_mock(**{
        "get_all_users.return_value": None,
        "get_user_by_id.return_value": None,
        "get_users_by_type.return_value": None,
        "search_sellers.return_value": None,
        "create_new_user.return_value": None,
        "verify_user.return_value": None,
        "resend_verification_email.return_value": None,
        "edit_user.return_value": None,
        "delete_user.return_value": None
    })
    return controller


@pytest_asyncio.fixture
async def test_app(
        test_session: AsyncSession,
        mock_user_service: Any,
        mock_user_controller: Any,
        test_user_id: str,
        test_user_email: str
) -> AsyncGenerator[FastAPI, None]:
    app = FastAPI(
        title="Test API",
        openapi_url=None,
        docs_url=None,
        redoc_url=None
    )

    from routers.user_router import router as user_router
    app.include_router(user_router)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    async def override_get_current_user(request: Request) -> dict:
        token = request.cookies.get(http_only_auth_cookie)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        try:
            if token == "invalid_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            if token == "expired_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            return {
                "email": test_user_email,
                "user_id": UUID(test_user_id)
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_user_controller] = lambda: mock_user_controller
    app.dependency_overrides[get_current_user] = override_get_current_user

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            app=test_app,
            base_url="http://test",
            follow_redirects=False,
    ) as client:
        yield client
