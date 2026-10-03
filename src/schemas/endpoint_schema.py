# Typing dependecies
from pydantic import (
    BaseModel, 
    JsonValue,
    Field,
    ConfigDict
)
from datetime import datetime
# Helper classes
from src.models.helpers.handle_scenario import HandleScenario
from src.models.helpers.methods import HttpMethods


# GET schema
class EndpointResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    # Endpoint's ID
    id: int
    # Endpoint's project (if exists)
    project_id: int | None
    # Endpoint method
    method: HttpMethods
    # Endpoint path
    path: str
    # HTTP status code
    status_code: int
    # HTTP response
    response_headers: dict[str, str]
    response_body: JsonValue | None
    # Handle scenario
    scenario: HandleScenario
    # Current endpoint status
    is_active: bool
    # Timestamps
    created_at: datetime
    updated_at: datetime | None

# POST schema
class EndpointCreate(BaseModel):
    # Endpoint's project (if exists)
    project_id: int | None = None
    # Endpoint method
    method: HttpMethods
    # Endpoint path
    path: str = Field(min_length=1, max_length=512)
    # HTTP status code
    status_code: int = Field(ge=100, le=599)
    # HTTP response
    response_headers: dict[str, str] = Field(default_factory=dict)
    response_body: JsonValue | None = None
    # Handle scenario
    scenario: HandleScenario = HandleScenario.SUCCESS # (successfull scenario by default)
    # Current endpoint status
    is_active: bool = True

# PUT/PATCH schema
class EndpointUpdate(BaseModel):
    # Endpoint's project (if exists)
    project_id: int | None = None
    # Endpoint method
    method: HttpMethods | None = None
    # Endpoint path
    path: str | None = Field(default=None, min_length=1, max_length=512)
    # HTTP status code
    status_code: int | None = Field(default=None, ge=100, le=599)
    # HTTP response
    response_headers: dict[str, str] | None = Field(default_factory=dict)
    response_body: JsonValue | None = None
    # Handle scenario
    scenario: HandleScenario | None = None
    # Current endpoint status
    is_active: bool | None = None
