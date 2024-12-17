import sys
from datetime import datetime, timedelta
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from config.parser import load_config
from models.database import Base, build_session_maker
from dependencies import get_session
from routers.user_router import get_user_controller, get_user_service
import logging
from dotenv import load_dotenv
import os
from unittest.mock import AsyncMock

logger = logging.getLogger(__name__)


def get_test_db_url() -> str:
    """Get test database URL from environment variables"""
    load_dotenv(".env.test")
    test_db_config = {
        "username": os.getenv("TEST_POSTGRES_USER"),
        "password": os.getenv("TEST_POSTGRES_PASSWORD"),
        "host": os.getenv("TEST_POSTGRES_HOST"),
        "port": os.getenv("TEST_POSTGRES_PORT"),
        "database": os.getenv("TEST_POSTGRES_DB"),
    }
    assert all(test_db_config.values()), "Missing test database environment variables!"

    return (
        f"postgresql+asyncpg://{test_db_config['username']}:{test_db_config['password']}"
        f"@{test_db_config['host']}:{test_db_config['port']}/{test_db_config['database']}"
    )


@pytest.fixture
def test_db_url():
    """Function-scoped fixture for database URL"""
    return get_test_db_url()


@pytest.fixture
def setup_test_env(monkeypatch, test_db_url):
    """Function-scoped fixture for environment setup"""
    monkeypatch.setenv("TEST_DATABASE_URL", test_db_url)
    return test_db_url


@pytest_asyncio.fixture
async def test_engine(setup_test_env):
    """Create and configure a test database engine"""
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


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    session_maker = build_session_maker(test_engine)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def mock_user_service():
    """Create a mock user service"""
    service = AsyncMock()
    return service


@pytest_asyncio.fixture
async def mock_user_controller():
    """Create a mock user controller that returns None by default to avoid recursion"""
    controller = AsyncMock()
    controller.configure_mock(**{
        "get_all_users.return_value": None,
        "get_user_by_id.return_value": None,
        "get_users_by_type.return_value": None,
        "search_sellers.return_value": None,
        "create_new_user.return_value": None,
        "verify_user.return_value": None,
        "resend_verification_email.return_value": None
    })
    return controller


@pytest_asyncio.fixture
async def test_app(
        test_session: AsyncSession,
        mock_user_service: Any,
        mock_user_controller: Any
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

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_user_controller] = lambda: mock_user_controller

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
    """Create an async HTTP client"""
    async with AsyncClient(
            app=test_app,
            base_url="http://test",
            follow_redirects=False,
    ) as client:
        yield client
