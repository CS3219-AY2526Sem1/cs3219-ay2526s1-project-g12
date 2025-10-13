from pydantic import BaseModel, Field
from typing import Annotated

class MatchRequest(BaseModel):
    user_id: Annotated[str, Field(min_length=1)]
    difficulty: Annotated[str, Field(min_length=1)]
    category: Annotated[str, Field(min_length=1)]
