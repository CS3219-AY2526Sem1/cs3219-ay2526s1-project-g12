from pydantic import BaseModel, Field
from typing import Annotated

class MatchData(BaseModel):
    data: Annotated[str, Field(min_length=0)]
