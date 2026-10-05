# Repositories
from src.repositories.endpoint_repository import EndpointRepository
# Schemas
from src.schemas.endpoint_schema import (
    EndpointCreate, 
    EndpointUpdate
    )
# Typing
from sqlalchemy.orm import Session
from fastapi import (
    HTTPException, 
    status
    )
# Models
from src.models.endpoint import Endpoint
# Exceptions
from sqlalchemy.exc import IntegrityError
# HTTP methods helper class
from src.models.helpers.methods import HttpMethods
# Handle scenario
from src.models.helpers.handle_scenario import HandleScenario


class EndpointService:
    def __init__(self, session: Session, endpoint_repo: EndpointRepository):
        self.session = session
        self.endpoint_repo = endpoint_repo

    # Get concrete endpoint by it's ID
    def get_endpoint_by_id(self, id: int) -> Endpoint:
        """Returns concrete Endpoint object by it's ID.

        Get concrete Endpoint object by given ID

        Parameters:
        id (int): Endpoint's id
    
        Returns:
        Endpoint: Found by ID Endpoint object
        """
        # Endpoint object
        endpoint = self.endpoint_repo.get_by_id(id)
        # Existance check
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint with that ID not found",
            )
        
        return endpoint

    # Get concrete endpoint by it's project_id, method, path, scenario
    def get_endpoint_by_params(
            self,
            project_id: int | None,
            method: HttpMethods,
            path: str,
            scenario: HandleScenario
    ) -> Endpoint:
        """Returns Endpoint object with by given set of parameters

        Parameters:
        project_id(int): Endpoint's project id
        
        method(HttpMethods(str)): Endpoint's (request) method
        
        path(str): Request url
        
        scenario(HandleScenario(str)): Handle scenario (success/failure, etc)

        Returns:
        Endpoint: Endpoint object
        """
        endpoint = self.endpoint_repo.get_by_route(
            project_id=project_id,
            method=method,
            path=path,
            scenario=scenario,
        )

        # Existance check
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint with this set of parameters is not found"
            )
        return endpoint

    # Get all endpoint (for future(maybe))
    def get_all_endpoints(self) -> list[Endpoint]:
        """Returns list of all Endpoints objects in database.

        Get all Endpoint objects in database
    
        Returns:
        list[Endpoint]: Endpoint objects
        """
        # List of Endpoint objects
        endpoints = self.endpoint_repo.get_all()

        # Existance check
        if not endpoints:
            return []

        return endpoints

    # Create new endpoint
    def create_endpoint(
        self,
        endpoint_data: EndpointCreate,
    ) -> Endpoint:
        """Creates Endpoint object with given data.

        Parameters:
        endpoint_data (EndpointCreate): New endpoint data
    
        Returns:
        Endpoint: Created Endpoint object
        """
        try:
            # New endpoint object
            new_endpoint =  self.endpoint_repo.create(endpoint_data)

            # Session commit and refresh new endpoint's data
            self.session.commit()
            self.session.refresh(new_endpoint)

            return new_endpoint
        except IntegrityError:
            # Rolling back failed transaction
            self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Endpoint with this combination of parameters already exists"
            )

    # Update concrete endpoint
    def update_endpoint(
        self,
        id: int,
        new_data: EndpointUpdate,
    ) -> Endpoint:
        """Update concrete Endpoint object by it's ID.

        Update concrete Endpoint object by it's ID with given data
        And returns it updated object

        Parameters:
        id (int): Endpoint's id
        new_data (EndpointUpdate): Updated endpoint's new data
    
        Returns:
        Endpoint: Updated Endpoint object
        """
        try:
            # Endpoint object to change
            endpoint = self.get_endpoint_by_id(id)
            changed_endpoint = self.endpoint_repo.update(
                id=endpoint.id, 
                endpoint_data=new_data
            )

            # Session commit and refresh changed endpoint's data
            self.session.commit()
            self.session.refresh(changed_endpoint)

            return changed_endpoint
        except IntegrityError:
            # Rolling back failed session transaction
            self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Endpoint with this combination of (project_id, method, scenario, path) already exists"
            )

    # Delete concrete endpoint by it's id
    def delete_endpoint(self, id: int) -> None:
        """Delete concrete Endpoint object by it's ID.

        Parameters:
        id (int): Endpoint's (object to delete) id
    
        Returns:
        None
        """

        # Endpoint object to delete
        endpoint = self.get_endpoint_by_id(id)
        self.endpoint_repo.delete(endpoint)

        self.session.commit()
