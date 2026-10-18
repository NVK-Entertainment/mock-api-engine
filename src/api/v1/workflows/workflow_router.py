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
)
# Annotation
from typing import Annotated


# Api router object
router = APIRouter(prefix='/api/v1')


@router.post(
    '/endpoints/{endpoint_id}/move-to/projects/{project_id}',
    status_code=status.HTTP_200_OK,
)
async def move_endpoint(
    endpoint_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
    project_id: int | None = None
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
    return await service.move_endpoint_to(
        endpoint_id, 
        project_id
    )

# Override endpoint from global to project scope
@router.post(
    '/endpoints/{endpoint_id}/clone-to/projects/{project_id}',
    status_code=status.HTTP_201_CREATED,
)
async def clone_endpoint(
    endpoint_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
    project_id: int | None = None,
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
    return await service.clone_endpoint_to(
        endpoint_id, 
        project_id
    )
