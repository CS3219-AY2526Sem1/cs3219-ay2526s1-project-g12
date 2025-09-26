import uuid
from typing import Annotated
from fastapi_users import schemas

from pydantic import Field


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    role_id: Annotated[int, Field(gt=0)]


class UserCreate(schemas.BaseUserCreate):
    password: Annotated[str, Field(min_length=8)]
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    role_id: Annotated[int, Field(gt=0)]


class UserUpdate(schemas.BaseUserUpdate):
    password: Annotated[str | None, Field(min_length=8)] = None
    first_name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    role_id: Annotated[int | None, Field(gt=0)] = None
