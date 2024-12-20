import asyncio
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from alembic import context
from config.parser import load_config
from models.database import Base
from models.models import *

# Load configurations
config = context.config
app_config = load_config()

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get target metadata
target_metadata = Base.metadata

# Define database URLs
DATABASE_URLS = [
    app_config.db_config.url,  # Production DB
    app_config.test_db_config.url,  # Test DB
]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    for url in DATABASE_URLS:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


async def run_migrations_for_engine(url: str) -> None:
    """Run migrations for a specific database URL."""
    configuration = {
        "sqlalchemy.url": url,
        "sqlalchemy.future": True,
    }

    engine = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Create alembic_version table if it doesn't exist
    async with engine.connect() as connection:
        await connection.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """
            )
        )
        await connection.commit()

        await connection.run_sync(_run_migrations)

    await engine.dispose()


def _run_migrations(connection: Connection) -> None:
    """Run actual migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations on all databases."""
    for url in DATABASE_URLS:
        await run_migrations_for_engine(url)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
