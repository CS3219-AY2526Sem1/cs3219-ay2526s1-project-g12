from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from auth.user_manager import UserManager
from db.models import AccessToken, User
from db.session import get_async_session


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
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

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
