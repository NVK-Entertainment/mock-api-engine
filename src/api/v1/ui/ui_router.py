# Fastapi
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
# Typing
from typing import Annotated
import json
# Services
from src.services.endpoint_service import EndpointService
from src.services.project_service import ProjectService
from src.core.factories import get_endpoint_service, get_project_service
# Helpers
from src.core.dependencies import BASE_DIR
from src.models.helpers.methods import HttpMethods
from src.models.helpers.handle_scenario import HandleScenario
from src.models.endpoint import Endpoint
from src.models.project import Project
from fastapi import HTTPException


# Jinja2 templates
templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')
templates.env.globals.update(
    METHODS=[m.value for m in HttpMethods],
    SCENARIOS=[s.value for s in HandleScenario],
    SHORT_METHODS={'DELETE': 'DEL', 'OPTIONS': 'OPT'},
)

# Api router object (HTML pages, not shown in OpenAPI schema)
router = APIRouter(prefix='/ui', include_in_schema=False)

_METHOD_ORDER = [m.value for m in HttpMethods]


def _sort_endpoints(endpoints: list[Endpoint]) -> list[Endpoint]:
    return sorted(
        endpoints,
        key=lambda e: (
            e.path,
            _METHOD_ORDER.index(e.method.value),
            e.scenario.value,
        ),
    )


def _base_context(
    projects: list[Project],
    endpoints: list[Endpoint],
    selected_id: int | None = None,
) -> dict:
    """Data for the sidebar tree and for the page scripts."""
    projects = sorted(projects, key=lambda p: p.name.lower())
    groups = [{
        'key': 'global',
        'project': None,
        'endpoints': _sort_endpoints([e for e in endpoints if e.project_id is None]),
    }]
    for project in projects:
        groups.append({
            'key': f'p{project.id}',
            'project': project,
            'endpoints': _sort_endpoints([e for e in endpoints if e.project_id == project.id]),
        })
    return {
        'groups': groups,
        'selected_id': selected_id,
        'app_data': {
            'projects': [{'id': p.id, 'name': p.name} for p in projects],
            'endpoints': [
                {
                    'id': e.id,
                    'project_id': e.project_id,
                    'method': e.method.value,
                    'path': e.path,
                }
                for e in endpoints
            ],
        },
    }


def _editor_context(endpoint: Endpoint | None, project: Project | None) -> dict:
    """Data for the endpoint editor form."""
    if endpoint is None:
        return {
            'id': None,
            'project_id': project.id if project else None,
            'scope_name': project.name if project else 'Глобальные',
            'method': 'GET',
            'path': '',
            'status_code': 200,
            'scenario': 'SUCCESS',
            'is_active': True,
            'headers': {},
            'body_text': '{}',
        }
    return {
        'id': endpoint.id,
        'project_id': endpoint.project_id,
        'scope_name': project.name if project else 'Глобальные',
        'method': endpoint.method.value,
        'path': endpoint.path,
        'status_code': endpoint.status_code,
        'scenario': endpoint.scenario.value,
        'is_active': endpoint.is_active,
        'headers': endpoint.response_headers,
        'body_text': (
            ''
            if endpoint.response_body is None
            else json.dumps(endpoint.response_body, ensure_ascii=False, indent=2)
        ),
    }


@router.get('', response_class=HTMLResponse)
async def ui_index(
    request: Request,
    endpoint_service: Annotated[EndpointService, Depends(get_endpoint_service)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
):
    """Main page: sidebar and empty state."""
    context = _base_context(
        await project_service.get_all_projects(),
        await endpoint_service.get_all_endpoints(),
    )
    return templates.TemplateResponse(request, 'index.html', context)


# Must be declared before '/endpoints/{endpoint_id}' to win over the int path param
@router.get('/endpoints/new', response_class=HTMLResponse)
async def ui_new_endpoint(
    request: Request,
    endpoint_service: Annotated[EndpointService, Depends(get_endpoint_service)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    project_id: int | None = None,
):
    """Form for a new endpoint (global scope or inside a project)."""
    projects = await project_service.get_all_projects()
    project = next((p for p in projects if p.id == project_id), None)
    if project_id is not None and project is None:
        return RedirectResponse('/ui')

    context = _base_context(projects, await endpoint_service.get_all_endpoints())
    context['editor'] = _editor_context(None, project)
    return templates.TemplateResponse(request, 'editor.html', context)


@router.get('/endpoints/{endpoint_id}', response_class=HTMLResponse)
async def ui_endpoint(
    endpoint_id: int,
    request: Request,
    endpoint_service: Annotated[EndpointService, Depends(get_endpoint_service)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
):
    """Editor of an existing endpoint."""
    try:
        endpoint = await endpoint_service.get_endpoint_by_id(endpoint_id)
    except HTTPException:
        # Endpoint was deleted (e.g. in another tab) - go back to the main page
        return RedirectResponse('/ui')

    projects = await project_service.get_all_projects()
    project = next((p for p in projects if p.id == endpoint.project_id), None)

    context = _base_context(
        projects,
        await endpoint_service.get_all_endpoints(),
        selected_id=endpoint.id,
    )
    context['editor'] = _editor_context(endpoint, project)
    return templates.TemplateResponse(request, 'editor.html', context)
