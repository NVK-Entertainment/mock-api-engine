from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.endpoint import Endpoint
from src.schemas.endpoint_schema import EndpointCreate
from src.models.helpers.methods import HttpMethods
from src.models.helpers.handle_scenario import HandleScenario
from src.schemas.endpoint_schema import EndpointUpdate


class EndpointRepository:
    def __init__(self, session: Session):
        self.session = session

    # Get concrete endpoint by it's id
    def get_by_id(self, id: int) -> Endpoint:
        # SQL statement
        stmt = (
            select(Endpoint)
            .where(Endpoint.id == id)
        )
        result = self.session.execute(stmt)

        # Endpoint object
        endpoint = result.scalars().one_or_none()

        return endpoint

    # Get concrete endpoint by it's path
    def get_by_route(
            self,
            project_id: int | None,
            method: HttpMethods,
            path: str,
            scenario: HandleScenario,
            ) -> Endpoint:
        # SQL statement
        stmt = (
            select(Endpoint)
            .where(
                Endpoint.project_id == project_id,
                Endpoint.method == method,
                Endpoint.path == path,
                Endpoint.scenario == scenario,
                Endpoint.is_active.is_(True),
                )
        )
        result = self.session.execute(stmt)

        # Endpoint object
        endpoint = result.scalars().first()

        return endpoint

    # Get all api endpoints (for future (maybe))
    def get_all(self) -> list[Endpoint]:
        # SQL statement
        stmt = (
            select(Endpoint)
        )
        result = self.session.execute(stmt)

        # List of Endpoint objects
        endpoints = result.scalars().all()

        return endpoints

    # Add endpoint to database
    def create(self, endpoint_data: EndpointCreate) -> Endpoint:
        # New endpoint object
        new_endpoint = Endpoint(
            project_id = endpoint_data.project_id,
            method = endpoint_data.method,
            path = endpoint_data.path,
            status_code = endpoint_data.status_code,
            scenario = endpoint_data.scenario,
            response_headers = endpoint_data.response_headers,
            response_body = endpoint_data.response_body,
            is_active = endpoint_data.is_active,
        )

        # Addition to local session list
        self.session.add(new_endpoint)

        return new_endpoint

    # Update concrete endpoint by it's id
    def update(
            self, 
            id: int, 
            endpoint_data: EndpointUpdate
        ) -> Endpoint | None:
        # Endpoint object by it's id
        endpoint = self.get_by_id(id)

        if endpoint is None:
            return None

        # Endpoint's new data
        update_data = endpoint_data.model_dump(exclude_unset=True)

        # Sets updated values (if given) to endpoint's fields
        for field, value in update_data.items():
            setattr(endpoint, field, value,)

        return endpoint

    # Delete concrete endpoint
    def delete(self, endpoint: Endpoint) -> None:        
        self.session.delete(endpoint)
