from pydantic import (
    BaseModel, 
    ConfigDict,
    Field,
)

class ProjectExport(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(min_length=1, max_length=32)
