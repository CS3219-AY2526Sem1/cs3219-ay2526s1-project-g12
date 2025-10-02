import uuid

from fastapi import APIRouter, Depends
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users import FastAPIUsers

from service.db_svc import get_user_manager, get_access_token_db
from models.api_models import UserCreate, UserRead, UserUpdate
from models.db_models import User, AccessToken
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

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

router = APIRouter()
router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=False),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=False),
    prefix="/users",
    tags=["users"],
)
