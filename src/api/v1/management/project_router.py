# Fastapi
from fastapi import (
    APIRouter, 
    status, 
    Depends
)
# Services
from src.services.project_service import ProjectService
from src.core.factories import get_project_service
# Schemas
from src.schemas.project_schema import (
    ProjectResponse,
    ProjectCreate,
    ProjectUpdate,
)
# Annotation
from typing import Annotated


# Api router object
router = APIRouter()


@router.get(
    '/projects', 
    response_model=list[ProjectResponse], 
    status_code=status.HTTP_200_OK,
)
def get_projects(
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> list[ProjectResponse]:
    """Get all projects API handle.

    Returns list of all projects in database.

    Parameters:
    service (ProjectService): ProjectService instance
    
    Returns:
    list[ProjectResponse]: List of project objects
    """
    return service.get_all_projects()


@router.get(
    '/projects/{project_id}', 
    response_model=ProjectResponse, 
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: int,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Get concrete project by its ID API handle.

    Returns concrete Project object by its ID.

    Parameters:
    service (ProjectService): ProjectService instance
    
    Returns:
    ProjectResponse: Concrete Project object by its ID
    """
    return service.get_project_by_id(project_id)


@router.post(
    '/projects', 
    response_model=ProjectResponse, 
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Create project with given data API handle.

    Creates new Project object with given data and returns it.

    Parameters:
    service (ProjectService): ProjectService instance
    
    Returns:
    ProjectResponse: Created Project object
    """
    return service.create_project(project_data)


@router.patch(
    '/projects/{project_id}',
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
def update_project_partially(
    project_id: int,
    project_data: ProjectUpdate,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Partially update concrete project by it's ID with given data API handle.

    Get concrete Project object by given ID and updates it with given data 
    then returns it.

    Parameters:
    service (ProjectService): ProjectService instance
    
    Returns:
    ProjectResponse: Partially updated Project object
    """
    return service.update_project(project_id, project_data)

@router.delete(
    '/projects/{project_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> None:
    """Delete concrete Project object by it's ID API handle.

    Get concrete Project object by given ID and delete it

    Parameters:
    service (ProjectService): ProjectService instance
    
    Returns:
    None
    """
    service.delete_project(project_id)