from pydantic import BaseModel, Field
from typing import Annotated

class MatchRequest(BaseModel):
    difficulty: Annotated[str, Field(min_length=1)]
    category: Annotated[str, Field(min_length=1)]
