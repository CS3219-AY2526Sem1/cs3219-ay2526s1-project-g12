from typing import Annotated

from fastapi import Cookie, HTTPException, Response

from utils.logger import log
from utils.utils import get_envvar

DEFAULT_COOKIE_MAX_AGE = int(get_envvar("DEFAULT_COOKIE_MAX_AGE"))


def _manage_access_token_cookie(
    response: Response, token: str, expiration_seconds: int, action: str
):
    """
    Private helper function to set or extend the access_token cookie.
    This function contains the shared logic for setting cookie properties and logging.
    """
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=True,
        samesite="none",  # "strict" is more secure but can affect UX
        max_age=int(expiration_seconds), 
    )

    log.info(f"{action} access_token cookie. Expires in: {expiration_seconds} seconds")
    


async def get_token(access_token: Annotated[str | None, Cookie()] = None) -> str:
    """
    Dependency to extract the access token from the browser cookie.
    Raises a 401 error if the cookie is not found.
    """
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated: Access token cookie not found.",
        )
    return access_token


async def set_access_token_cookie(
    response: Response, token: str, expiration_seconds: int = DEFAULT_COOKIE_MAX_AGE
):
    """
    Sets a new 'access_token' cookie after an event like login.
    """
    _manage_access_token_cookie(response, token, expiration_seconds, action="Set")
    return token


async def extend_access_token_cookie(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
    expiration_seconds: int = DEFAULT_COOKIE_MAX_AGE,
):
    """
    Extends the 'access_token' cookie expiration if it exists.
    """
    if not access_token:
        return None

    _manage_access_token_cookie(response, access_token, expiration_seconds, action="Extended")
    return access_token
