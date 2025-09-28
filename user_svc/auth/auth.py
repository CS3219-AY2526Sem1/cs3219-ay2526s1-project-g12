from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from auth.dependencies import get_access_token_db
from db.models import AccessToken

cookie_transport = CookieTransport(
    cookie_max_age=3600,
    cookie_name="fastapiusersauth",  # Default cookie name
    cookie_path="/",
    cookie_domain=None,
    cookie_secure=False,  # Set to True in production with HTTPS
    cookie_httponly=True,  # Prevents JavaScript access (security)
    cookie_samesite="lax"
)
def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="database",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
