from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import User
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

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get the user database.

    Args:
        session (AsyncSession, optional): The database session. Defaults to Depends(get_async_session).

    Yields:
        SQLAlchemyUserDatabase: The user database.
    """
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
):
    """Get the access token database.

    Args:
        session (AsyncSession, optional): The database session. Defaults to Depends(get_async_session).

    Yields:
        SQLAlchemyAccessTokenDatabase: The access token database.
    """
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
