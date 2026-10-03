# Typing dependecies
from pydantic import (
    BaseModel, 
    Field
)


# GET schema
class ProjectResponse(BaseModel):
    id: int
    name: str

# POST schema
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=32)

# PUT/PATCH schema
class ProjectUpdate(BaseModel):
    name: str | None = None
