from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_models import User
from service.db_session_svc import get_async_session


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
