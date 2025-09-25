from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from utils.utils import get_envvar

DATABASE_URL = get_envvar("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an asynchronous database session.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    async with async_session_maker() as session:
        yield session
