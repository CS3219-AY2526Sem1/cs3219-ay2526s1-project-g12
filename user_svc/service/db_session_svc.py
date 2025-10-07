from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from utils.utils import AppConfig

config = AppConfig()

DATABASE_URL = str(config.database_url)
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an asynchronous database session.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    async with async_session_maker() as session:
        yield session
