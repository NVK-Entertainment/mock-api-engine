from src.services.endpoint_service import EndpointService
from src.repositories.endpoint_repository import EndpointRepository
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
    
    return EndpointService(
        session=session,
        endpoint_repo=endpoint_repo,
    )
