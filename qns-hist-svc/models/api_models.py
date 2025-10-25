from typing import Annotated

from annotated_types import Len
from pydantic import BaseModel, Field


class CreateQuestionModel(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    code_template: Annotated[str, Field(min_length=1)]
    solution_sample: Annotated[str, Field(min_length=1)]
    difficulty: Annotated[str, Field(min_length=1)]
    category: Annotated[list[str], Len(min_length=1)]
    submitted_solution: Annotated[str, Field(min_length=1)]
