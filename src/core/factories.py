# Services
from src.services.endpoint_service import EndpointService
from src.services.project_service import ProjectService
from src.services.file_handlers.endpoint_export_service import EndpointExportService
from src.services.file_handlers.projects_export_service import ProjectExportService

# Repositories
from src.repositories.endpoint_repository import EndpointRepository
from src.repositories.project_repository import ProjectRepository

# Annotation
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

# Session DI
from fastapi import Depends
from src.database.db import get_session


def get_endpoint_service(session: Annotated[AsyncSession, Depends(get_session)]) -> EndpointService:
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

def get_project_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ProjectService:
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

def get_endpoint_export_service(session: Annotated[AsyncSession, Depends(get_session)]) -> EndpointExportService:
    """ Endpoint export service factory
    
        Parameters:
        session (Session): Database connection session instance

        Returns:  
        EndpointExportService: EndpointExportService instance within one session
    """
    endpoint_service = get_endpoint_service(session)

    return EndpointExportService(
        session=session,
        endpoint_service=endpoint_service
    )

def get_project_export_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ProjectExportService:
    """ Project export service factory
    
        Parameters:
        session (Session): Database connection session instance

        Returns:  
        ProjectExportService: ProjectExportService instance within one session
    """
    endpoint_service = get_endpoint_service(session)
    project_service = get_project_service(session)

    return ProjectExportService(
        session=session,
        endpoint_service=endpoint_service,
        project_service=project_service,
    )
