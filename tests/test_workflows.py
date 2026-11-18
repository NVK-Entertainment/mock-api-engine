# HTTP requests
from httpx import AsyncClient
# Url constants
from tests.conftest import ENDPOINTS_URL


WORKFLOWS_URL = '/api/v1/endpoints'


async def test_move_endpoint_to_project(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Target')
    endpoint = await create_endpoint(method='GET', path='/api/nomad')

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/move-to/projects/{project['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == endpoint['id']
    assert data['project_id'] == project['id']


async def test_move_endpoint_to_unknown_project(client: AsyncClient, create_endpoint):
    endpoint = await create_endpoint(method='GET', path='/api/lost')

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/move-to/projects/999999")

    assert response.status_code == 404


async def test_move_endpoint_conflict_with_active(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Busy')
    global_endpoint = await create_endpoint(method='GET', path='/api/clash')
    await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/clash',
    )

    response = await client.post(f"{WORKFLOWS_URL}/{global_endpoint['id']}/move-to/projects/{project['id']}")

    assert response.status_code == 409


async def test_move_endpoint_reactivates_inactive(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Revive')
    global_endpoint = await create_endpoint(method='GET', path='/api/reborn')
    inactive = await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/reborn',
        is_active=False,
    )

    response = await client.post(f"{WORKFLOWS_URL}/{global_endpoint['id']}/move-to/projects/{project['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == inactive['id']
    assert data['is_active'] is True
    assert data['project_id'] == project['id']
    assert (await client.get(f"{ENDPOINTS_URL}/{global_endpoint['id']}")).status_code == 404


async def test_clone_endpoint_to_project(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Copied')
    endpoint = await create_endpoint(
        method='GET',
        path='/api/cloneable',
        status_code=200,
        response_body={'origin': True},
    )

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/clone-to/projects/{project['id']}")

    assert response.status_code == 201
    data = response.json()
    assert data['id'] != endpoint['id']
    assert data['project_id'] == project['id']
    assert data['path'] == '/api/cloneable'
    assert data['response_body'] == {'origin': True}
    assert (await client.get(f"{ENDPOINTS_URL}/{endpoint['id']}")).status_code == 200


async def test_clone_endpoint_conflict_with_active(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Conflict')
    endpoint = await create_endpoint(method='GET', path='/api/twice')
    await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/twice',
    )

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/clone-to/projects/{project['id']}")

    assert response.status_code == 409


async def test_promote_endpoint_to_global(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Promoted')
    endpoint = await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/rocket',
        status_code=200,
        response_body={'promoted': True},
    )

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/promote-to-global")

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == endpoint['id']
    assert data['project_id'] is None


async def test_promote_endpoint_conflict_with_active_global(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Blocked')
    await create_endpoint(method='GET', path='/api/occupied')
    endpoint = await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/occupied',
    )

    response = await client.post(f"{WORKFLOWS_URL}/{endpoint['id']}/promote-to-global")

    assert response.status_code == 409


async def test_promote_endpoint_unknown(client: AsyncClient):
    response = await client.post(f'{WORKFLOWS_URL}/999999/promote-to-global')

    assert response.status_code == 404
