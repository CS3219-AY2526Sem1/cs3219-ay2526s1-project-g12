from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from auth.dependencies import get_access_token_db
from models.db_models import AccessToken
from utils.utils import AppConfig

config = AppConfig()

cookie_transport = CookieTransport(
    cookie_max_age=config.access_token_expire_seconds,
    cookie_name=config.cookie_name,
    cookie_path="/",
    cookie_domain=None,
    cookie_secure=False,  # Set to True in production with HTTPS
    cookie_httponly=True,  # Prevents JavaScript access (security)
    cookie_samesite="lax"
)
def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    """Provides the database strategy for authentication.

    Args:
        access_token_db (AccessTokenDatabase[AccessToken]): The access token database dependency.

    Returns:
        DatabaseStrategy: The database strategy for authentication.
    """
    return DatabaseStrategy(access_token_db, lifetime_seconds=config.access_token_expire_seconds)

auth_backend = AuthenticationBackend(
    name="database",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
