from src.services.endpoint_service import EndpointService
from src.repositories.endpoint_repository import EndpointRepository
from src.services.project_service import ProjectService
from src.repositories.project_repository import ProjectRepository

from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends
from src.database.db import get_session


def get_endpoint_service(session: Annotated[Session, Depends(get_session)]) -> EndpointService:
    """ Endpoint service factory
        
        Get session instance and create EndpointRepository instance
        within one session

        Parameters:
        session (Session): Database connection session instance

        Returns:  
        EndpointService: EndpointService instance within one session 
    """
    # Endpoint repo instance
    endpoint_repo = EndpointRepository(session)
    project_service = get_project_service(session)
    
    return EndpointService(
        session=session,
        endpoint_repo=endpoint_repo,
        project_service=project_service
    )

def get_project_service(session: Annotated[Session, Depends(get_session)]) -> ProjectService:
    """ Project service factory
        
        Get session instance and create ProjectRepository instance
        within one session

        Parameters:
        session (Session): Database connection session instance

        Returns:  
        ProjectService: ProjectService instance within one session 
    """
    # Endpoint repo instance
    project_repo = ProjectRepository(session)
    
    return ProjectService(
        session=session,
        project_repo=project_repo,
    )