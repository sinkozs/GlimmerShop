from typing_extensions import AsyncGenerator
import redis.asyncio as aioredis
from config.parser import load_config
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)


def build_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_maker = async_sessionmaker(
        bind=engine, autoflush=True, expire_on_commit=True
    )
    return session_maker


async def get_redis() -> AsyncGenerator:
    redis_config = load_config().redis_config
    print(f"Redis URL: {redis_config.url}")
    redis = aioredis.from_url(redis_config.url, decode_responses=True, encoding="utf-8")
    try:
        yield redis
    finally:
        await redis.close()


async def build_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


class Base(AsyncAttrs, DeclarativeBase):
    pass
