from typing_extensions import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession
)


def build_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_maker = async_sessionmaker(bind=engine,
                                       autoflush=True,
                                       expire_on_commit=True)
    return session_maker


async def build_session(session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
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
