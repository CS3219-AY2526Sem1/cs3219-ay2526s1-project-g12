from typing import Annotated

from annotated_types import Len
from pydantic import BaseModel, Field


class CreateQuestionModel(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    difficulty: Annotated[str, Field(min_length=1)]
    categories: Annotated[list[str], Len(min_length=1)]


class UpdateQuestionModel(BaseModel):
    title: Annotated[str | None, Field(min_length=1)] = None
    description: Annotated[str | None, Field(min_length=1)] = None
    difficulty: Annotated[str | None, Field(min_length=1)] = None
    categories: Annotated[list[str] | None, Len(min_length=1)] = None
