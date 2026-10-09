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


@router.get(
    '/endpoints', 
    response_model=list[EndpointResponse], 
    status_code=status.HTTP_200_OK,
)
def get_endpoints(
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> list[EndpointResponse]:
    """Get all endpoint API handle.

    Returns list of all endpoints in database.

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    list[EndpointResponse]: List of endpoint objects
    """
    return service.get_all_endpoints()


@router.get(
    '/endpoints/{endpoint_id}', 
    response_model=EndpointResponse, 
    status_code=status.HTTP_200_OK,
)
def get_endpoint(
    endpoint_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> EndpointResponse:
    """Get concrete endpoint by its ID API handle.

    Returns concrete Endpoint object by its ID.

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    EndpointResponse: Concrete Endpoint object by its ID
    """
    return service.get_endpoint_by_id(endpoint_id)


@router.post(
    '/endpoints', 
    response_model=EndpointResponse, 
    status_code=status.HTTP_201_CREATED,
)
def create_endpoint(
    endpoint_data: EndpointCreate,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> EndpointResponse:
    """Create endpoint with given data API handle.

    Creates new Endpoint object with given data and returns it.

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    EndpointResponse: Created Endpoint object
    """
    return service.create_endpoint(endpoint_data)


@router.patch(
    '/endpoints/{endpoint_id}',
    response_model=EndpointResponse,
    status_code=status.HTTP_200_OK,
)
def update_endpoint_partially(
    endpoint_id: int,
    endpoint_data: EndpointUpdate,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> EndpointResponse:
    """Partially update concrete endpoint by it's ID with given data API handle.

    Get concrete Endpoint object by given ID and updates it with given data 
    then returns it.

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    EndpointResponse: Partially updated Endpoint object
    """
    return service.update_endpoint(endpoint_id, endpoint_data)


''' (Temporaly frozen till it's really needed)
@router.put(
    '/endpoints/{endpoint_id}',
    response_model=EndpointResponse,
    status_code=status.HTTP_200_OK,
)
def update_endpoint_fully(
    endpoint_id: int,
    endpoint_data: EndpointUpdate,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> EndpointResponse:
    """Fully update concrete endpoint by it's ID with given data API handle.

    Get concrete Endpoint object by given ID and updates it with given data
    Then returns it.
    If some fields wasn't given raises exception.

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    EndpointResponse: Fully updated Endpoint object
    """
    return service.update_endpoint(endpoint_id, endpoint_data)
'''


@router.delete(
    '/endpoints/{endpoint_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_endpoint(
    endpoint_id: int,
    service: Annotated[EndpointService, Depends(get_endpoint_service)],
) -> None:
    """Delete concrete Endpoint object by it's ID API handle.

    Get concrete Endpoint object by given ID and delete it

    Parameters:
    service (EndpointService): EndpointService instance
    
    Returns:
    None
    """
    service.delete_endpoint(endpoint_id)

