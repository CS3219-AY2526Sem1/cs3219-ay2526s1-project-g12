import asyncio
import re
import uuid
from typing import Any, Dict, Optional, Union

from fastapi import Request, Response
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin

from models.api_models import UserCreate
from models.db_models import User
from service.mail_svc import send_password_reset_email, send_verification_email
from utils.logger import log
from utils.utils import AppConfig

config = AppConfig()


class UserController(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = config.reset_token_secret
    reset_password_token_lifetime_seconds = config.reset_token_expire_seconds
    verification_token_secret = config.verify_token_secret
    verification_token_lifetime_seconds = config.verify_token_expire_seconds

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        """Validates the password with the following rules:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number or symbol
        - Should not contain the e-mail address

        Args:
            password: Password string to validate
            user: User object or UserCreate object

        Raises:
            InvalidPasswordException: If the password is invalid
        """
        # Length check
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password must be at least 8 characters long."
            )
        # At least one uppercase
        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException(
                reason="Password must contain at least one uppercase letter."
            )
        # At least one lowercase
        if not re.search(r"[a-z]", password):
            raise InvalidPasswordException(
                reason="Password must contain at least one lowercase letter."
            )
        # At least one digit OR symbol
        if not re.search(r"[\d\W_]", password):
            raise InvalidPasswordException(
                reason="Password must contain at least one number or symbol."
            )
        # Disallow e-mail inside password for extra safety
        if getattr(user, "email", None) and user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain the e-mail address."
            )

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        log.info(f"User {user.id} has registered.")
        await self.request_verify(user, request)

    async def on_after_update(
        self,
        user: User,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ):
        log.info(f"User {user.id} has been updated with {update_dict}.")
        if "email" in update_dict:
            await self.request_verify(user, request)

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        log.info(f"User {user.id} logged in.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        log.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )
        asyncio.create_task(send_verification_email(user, token))

    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        log.info(f"User {user.id} has been verified.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        log.info(f"User {user.id} has forgot their password. Reset token: {token}")
        asyncio.create_task(send_password_reset_email(user, token))

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        log.info(f"User {user.id} has reset their password.")

    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        log.info(f"User {user.id} is going to be deleted.")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        log.info(f"User {user.id} is successfully deleted.")
