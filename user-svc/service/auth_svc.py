import uuid

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, AuthenticationBackend, JWTStrategy

from controllers.user_controller import UserController
from models.db_models import User
from service.db_svc import get_user_db
from utils.utils import AppConfig


config = AppConfig()

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserController(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/login")

def _get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.jwt_secret, lifetime_seconds=None)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=_get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
