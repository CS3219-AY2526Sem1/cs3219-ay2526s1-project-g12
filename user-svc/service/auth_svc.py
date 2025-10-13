import uuid
from typing import Optional, Annotated

from fastapi import Depends, Response, Header, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_users import FastAPIUsers, models, exceptions
from fastapi_users.authentication import BearerTransport, AuthenticationBackend, JWTStrategy, Authenticator, Strategy
from fastapi_users.authentication.authenticator import EnabledBackendsDependency
from fastapi_users.openapi import OpenAPIResponseType

from controllers.user_controller import UserController
from models.api_models import UuidBearerResponse
from models.db_models import User
from service.db_svc import get_user_db
from utils.utils import AppConfig


config = AppConfig()

async def get_user_manager(user_db=Depends(get_user_db)):
    """Dependency to get the user manager.

    Args:
        user_db: The user database dependency.

    Yields:
        An instance of UserController.
    """
    yield UserController(user_db)

def _get_jwt_strategy() -> JWTStrategy:
    """Method to get the JWT strategy for authentication.

    Returns:
        An instance of JWTStrategy with the configured secret and token lifetime.
    """
    return JWTStrategy(secret=config.jwt_secret, lifetime_seconds=1)


class UuidBearerTransport(BearerTransport):
    """Custom bearer transport that includes user_id in the login response."""
    async def get_login_response(self, token: str, **kwargs) -> Response:
        """Overridden method to include user_id in the response."""
        user_id = kwargs.get("user_id")
        role = kwargs.get("role")
        bearer_response = UuidBearerResponse(access_token=token, token_type="bearer", user_id=user_id, role=role)
        return JSONResponse(jsonable_encoder(bearer_response))

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        """Custom OpenAPI response schema including user_id."""
        return {
            status.HTTP_200_OK: {
                "model": UuidBearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "token_type": "bearer",
                            "user_id": "9e9b8b9f-98cd-4e0c-b8e1-8ef4fbc4e3b2",
                            "role": {"id": 1, "role": "user"},
                        }
                    }
                },
            },
        }


class UuidAuthenticationBackend(AuthenticationBackend[models.UP, models.ID]):
    """Custom authentication backend using UUIDs."""
    transport: UuidBearerTransport

    async def login(
            self, strategy: Strategy[User, uuid.UUID], user: User
    ) -> Response:
        """Overridden login method to include user_id in the response."""
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token, user_id=user.id, role=user.role)


class UuidAuthenticator(Authenticator[models.UP, models.ID]):
    """Custom authenticator to retrieve current user based on X-User-ID header."""
    def current_user(
            self,
            optional: bool = False,
            active: bool = False,
            verified: bool = False,
            superuser: bool = False,
            get_enabled_backends: Optional[
                EnabledBackendsDependency[models.UP, models.ID]
            ] = None,
    ):
        """Custom current user dependency that retrieves user based on X-User-ID header."""
        async def current_user_dependency(
                x_user_id: Annotated[uuid.UUID | None, Header(alias="X-User-ID")] = None,
                user_manager=Depends(self.get_user_manager),
        ):
            user: Optional[models.UP] = None
            if x_user_id is not None:
                try:
                    parsed_id = user_manager.parse_id(x_user_id)
                    user = await user_manager.get(parsed_id)
                except (exceptions.UserNotExists, exceptions.InvalidID):
                    pass

            status_code = status.HTTP_401_UNAUTHORIZED
            if user:
                status_code = status.HTTP_403_FORBIDDEN
                if active and not user.is_active:
                    status_code = status.HTTP_401_UNAUTHORIZED
                    user = None
                elif (
                        verified and not user.is_verified or superuser and not user.is_superuser
                ):
                    user = None

            if not user and not optional:
                raise HTTPException(status_code=status_code)
            return user

        return current_user_dependency

bearer_transport = UuidBearerTransport(tokenUrl="auth/login")

auth_backend = UuidAuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=_get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
fastapi_users.authenticator = UuidAuthenticator(
    [auth_backend], fastapi_users.get_user_manager
)
