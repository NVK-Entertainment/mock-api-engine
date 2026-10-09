# Fastapi
from fastapi import (
    APIRouter,  
    Depends,
    Request,
)
from fastapi.responses import JSONResponse
# Services
from src.services.endpoint_service import EndpointService
from src.core.factories import get_endpoint_service
# Annotation
from typing import Annotated
from src.models.helpers.methods import HttpMethods
from src.models.helpers.handle_scenario import HandleScenario


# Api router object
router = APIRouter()

def get_mock_response(
    path: str,
    request: Request,
    service: EndpointService,
    project_id: int | None = None,
) -> JSONResponse:
    """Global template

    Get Endpoint object by given set of parameters 
    And returns it's JSON mock response

    Parameters:

    project_id(int | None): Endpoint's project id
    
    method(HttpMethods(str)): Endpoint's (request) method
    
    path(str): Request url
    
    scenario(HandleScenario(str)): Handle scenario (success/failure, etc)
    
    service(EndpointService): Endpoint service instance

    Returns:
    JSONResponse: Endpoint's JSON HTTP-response
    """

    # Correct request URL
    complete_path = "/" + path.lstrip("/")
    
    # Request method
    method = HttpMethods(request.method)
    # Request scenario
    scenario_raw = (
        request.headers.get('X-mock-scenario')
        or HandleScenario.SUCCESS.value
    )

    # Scenario field check
    try:
        scenario = HandleScenario(scenario_raw)
    except ValueError:
        scenario = HandleScenario.SUCCESS


    # Endpoint object by it's parameters
    endpoint = service.get_endpoint_by_params(
        project_id=project_id,
        method=method,
        path=complete_path,
        scenario=scenario
    )
    # Mock handle response
    return JSONResponse(
        status_code=endpoint.status_code,
        headers=endpoint.response_headers,
        content=endpoint.response_body,
    )

@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.OPTIONS.value],
    operation_id='process_project_mock_options',
)
@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.PATCH.value],
    operation_id='process_project_mock_patch',
)
@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.PUT.value],
    operation_id='process_project_mock_put',
)
@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.DELETE.value],
    operation_id='process_project_mock_delete',
)
@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.POST.value],
    operation_id='process_project_mock_post',
)
@router.api_route(
    '/mock/{project_id}/{path:path}',
    methods=[HttpMethods.GET.value],
    operation_id='process_project_mock_get',
)
def process_project_mock(
    project_id: int,
    path: str,
    request: Request,
    service: Annotated[EndpointService, Depends(get_endpoint_service)]
) -> JSONResponse:
    """ Process mocks with project
        Implements get_mock_response template
    """
    return get_mock_response(
        project_id=project_id,
        path=path,
        request=request,
        service=service,
    )

@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.OPTIONS.value],
    operation_id='process_global_mock_options',
)
@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.PATCH.value],
    operation_id='process_global_mock_patch',
)
@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.PUT.value],
    operation_id='process_global_mock_put',
)
@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.DELETE.value],
    operation_id='process_global_mock_delete',
)
@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.POST.value],
    operation_id='process_global_mock_post',
)
@router.api_route(
    '/mock/{path:path}',
    methods=[HttpMethods.GET.value],
    operation_id='process_global_mock_get',
)
def process_global_mock(
    path: str,
    request: Request,
    service: Annotated[EndpointService, Depends(get_endpoint_service)]
) -> JSONResponse:
    """ Process mocks without project
        Implements get_mock_response template
    """
    return get_mock_response(
        project_id=None,
        path=path,
        request=request,
        service=service
    )
