from pydantic import (
    BaseModel, 
    ConfigDict,
    Field,
    JsonValue,
    field_validator
)
from src.core.utils import normalize_path
from src.models.helpers.methods import HttpMethods
from src.models.helpers.handle_scenario import HandleScenario


class EndpointExport(BaseModel):
    model_config = ConfigDict(extra='forbid')

    project_name: str | None = None
    method: HttpMethods
    path: str = Field(min_length=1, max_length=512)
    status_code: int = Field(ge=100, le=599)
    scenario: HandleScenario = HandleScenario.SUCCESS
    response_headers: dict[str, str]
    response_body: JsonValue | None = None
    is_active: bool

    @field_validator('path', mode='before')
    @classmethod
    def _normalize_path(cls, path: str) -> str:
        return normalize_path(path)
