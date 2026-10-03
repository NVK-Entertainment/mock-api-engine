# Fastapi
from fastapi import (
    APIRouter, 
    status, 
    Depends
)
# Services
from src.services.endpoint_service import EndpointService
from src.core.factories import get_endpoint_service
# Schemas
from src.schemas.endpoint_schema import (
    EndpointResponse,
    EndpointCreate,
    EndpointUpdate,
)
# Annotation
from typing import Annotated
from src.models.helpers.methods import HttpMethods

''' IN PROGRESS!
# Api router object
router = APIRouter(prefix='/mock')

@router.api_route(
    methods=[method.value for method in HttpMethods]
)
def process_mock_handle():
    pass
'''