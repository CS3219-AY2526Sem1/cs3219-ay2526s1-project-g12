from typing import Annotated

from annotated_types import Len
from pydantic import BaseModel, Field


class SubmitQuestionAttemptModel(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    code_template: Annotated[str, Field(min_length=1)]
    solution_sample: Annotated[str, Field(min_length=1)]
    difficulty: Annotated[str, Field(min_length=1)]
    category: Annotated[str, Len(min_length=1)]
    time_elapsed: Annotated[int, Field(gt=0)]
    submitted_solution: Annotated[str, Field(min_length=1)]
    users: Annotated[
        list[Annotated[str, Field(min_length=1)]], Field(min_length=2, max_length=2)
    ]
