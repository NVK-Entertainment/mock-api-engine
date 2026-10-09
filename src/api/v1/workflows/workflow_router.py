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


# Api router object
router = APIRouter()


# Promote endpoint to global scope
@router.post(
    '/projects/{project_id}/endpoints/{endpoint_id}/promote-to-global',
    status_code=status.HTTP_201_CREATED,
)
def move_endpoint(
    project_id: int,
    endpoint_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)]
) -> EndpointResponse:
    """Move concrete Endpoint object by it's ID to global or another project scope.

    Calling EndpointService method move_endpoint_to 
    To move endpoint record to another scope  

    Parameters:
    project_id (int | None): Where to move (global scope or another project scope)
    endpoint_id (int): Endpoint to move object ID

    Returns:
    Endpoint: Moved Endpoint object
    """
    return service.move_endpoint_to(
        endpoint_id, 
        project_id
    )

# Override endpoint from global to project scope
@router.post(
    '/endpoints/{endpoint_id}/projects/{project_id}',
    status_code=status.HTTP_201_CREATED,
)
def clone_endpoint(
    endpoint_id: int,
    project_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)]
) -> EndpointResponse:
    """Clone concrete Endpoint object by it's ID to global or another project scope.

    Calling EndpointService method "clone_endpoint_to" 
    To clone endpoint record to another scope  

    Parameters:
    project_id (int | None): Where to clone (global scope or another project scope)
    endpoint_id (int): Endpoint to clone object ID

    Returns:
    Endpoint: Cloned Endpoint object
    """
    return service.clone_endpoint_to(
        endpoint_id, 
        project_id
    )
