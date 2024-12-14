import sys
import uuid
from datetime import datetime, date, timezone

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from models.database import Base
import os

from main import main
from dependencies import get_session, hash_password
import logging
from dotenv import load_dotenv

# Allow imports from the backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set environment variables and build test DB URL for testing"""
    load_dotenv(".env.test")
    test_db_config = {
        "username": os.getenv("TEST_POSTGRES_USER"),
        "password": os.getenv("TEST_POSTGRES_PASSWORD"),
        "host": os.getenv("TEST_POSTGRES_HOST"),
        "port": os.getenv("TEST_POSTGRES_PORT"),
        "database": os.getenv("TEST_POSTGRES_DB"),
    }

    assert all(test_db_config.values()), "Missing test database environment variables!"

    test_db_url = (
        f"postgresql+asyncpg://{test_db_config['username']}:{test_db_config['password']}"
        f"@{test_db_config['host']}:{test_db_config['port']}/{test_db_config['database']}"
    )

    monkeypatch.setenv("TEST_DATABASE_URL", test_db_url)
    return test_db_url


@pytest_asyncio.fixture
async def test_engine():
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
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


# ====== FastAPI Application Setup ======
@pytest_asyncio.fixture
async def test_app(test_session) -> AsyncGenerator[FastAPI, None]:
    app = main()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    yield app


# ====== Async HTTP Client ======
@pytest_asyncio.fixture
async def async_test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client"""
    print(f"Using POSTGRES_PORT={os.getenv('POSTGRES_PORT')}")
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


# ====== Test Users ======
@pytest.fixture
def test_users() -> list[dict]:
    return [
        {
            "id": str(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb791")),
            "first_name": "John",
            "last_name": "Doe",
            "email": "seller@example.com",
            "hashed_password": hash_password("strongpassword"),
            "password_length": 14,
            "is_seller": True,
            "is_verified": True,
            "is_active": True,
            "last_login": datetime.now(),
            "registration_date": date.today()
        },
        {
            "id": str(uuid.UUID("7a4ae081-2f63-4653-bf67-f69a00dcb792")),
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "buyer@example.com",
            "hashed_password": hash_password("securepassword"),
            "password_length": 13,
            "is_seller": False,
            "is_verified": False,
            "is_active": False,
            "last_login": None,
            "registration_date": date.today()
        }
    ]
