import uuid
from typing import Annotated

from fastapi_users import schemas
from fastapi_users.authentication.transport.bearer import BearerResponse
from pydantic import BaseModel, ConfigDict, Field


class Role(BaseModel):
    """Class representing a user role.

    Attributes:
        id (int): The unique identifier of the role.
        role (str): The name of the role.
    """
    id: Annotated[int, Field(gt=0)]
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserRead(schemas.BaseUser[uuid.UUID]):
    """Class representing the user data to be read.

    Attributes:
        id (uuid): The unique identifier of the user.
        email (str): The email of the user.
        is_active (bool): Indicates if the user is active.
        is_superuser (bool): Indicates if the user has superuser privileges.
        is_verified (bool): Indicates if the user's email is verified.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        role (Role): The role of the user.
    """
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    role: Role


class UserCreate(schemas.BaseUserCreate):
    """Class representing the user data required for creation.

    Attributes:
        email (str): The email of the user.
        password (str): The password of the user, must be at least 8 characters long.
        first_name (str): The first name of the user, must be between 1 and 50 characters.
        last_name (str): The last name of the user, must be between 1 and 50 characters.
    """
    password: Annotated[str, Field(min_length=8)]
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]


class UserUpdate(schemas.BaseUserUpdate):
    """Class representing the user data that can be updated.

    Attributes:
        email (str | None): The new email of the user if provided.
        password (str | None): The new password of the user, must be at least 8 characters long if provided.
        first_name (str | None): The new first name of the user, must be between 1 and 50 characters if provided.
        last_name (str | None): The new last name of the user, must be between 1 and 50 characters if provided.
    """
    password: Annotated[str | None, Field(min_length=8)] = None
    first_name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class UuidBearerResponse(BearerResponse):
    """Class representing a bearer token response with user ID.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token, typically "Bearer".
        user_id (uuid): The unique identifier of the user associated with the token.
    """
    user_id: uuid.UUID
