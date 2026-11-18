# HTTP requests
from httpx import AsyncClient
# Url constants
from tests.conftest import ENDPOINTS_URL


MOCK_URL = '/api/v1/mock'
SCENARIO_HEADER = 'X-mock-scenario'


async def test_global_mock_returns_configured_response(client: AsyncClient, create_endpoint):
    await create_endpoint(
        method='GET',
        path='/api/users',
        status_code=201,
        response_body={'id': 1, 'name': 'Alice'},
        response_headers={'X-Custom': 'value'},
    )

    response = await client.get(f'{MOCK_URL}/api/users')

    assert response.status_code == 201
    assert response.json() == {'id': 1, 'name': 'Alice'}
    assert response.headers['X-Custom'] == 'value'
    assert response.headers['content-type'] == 'application/json'


async def test_global_mock_method_matters(client: AsyncClient, create_endpoint):
    await create_endpoint(method='POST', path='/api/users', status_code=201)

    response = await client.post(f'{MOCK_URL}/api/users')

    assert response.status_code == 201
    assert (await client.get(f'{MOCK_URL}/api/users')).status_code == 404


async def test_global_mock_unknown_path(client: AsyncClient):
    response = await client.get(f'{MOCK_URL}/api/nothing')

    assert response.status_code == 404


async def test_global_mock_path_normalization(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/data')

    response = await client.get(f'{MOCK_URL}/api/data/')

    assert response.status_code == 200
    assert response.json() == {'ok': True}


async def test_global_mock_inactive_endpoint(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/sleeping', is_active=False)

    response = await client.get(f'{MOCK_URL}/api/sleeping')

    assert response.status_code == 404


async def test_mock_scenario_failure(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/pay', status_code=200, response_body={'ok': True})
    await create_endpoint(
        method='GET',
        path='/api/pay',
        status_code=502,
        response_body={'error': 'upstream failed'},
        scenario='FAILURE',
    )

    response = await client.get(f'{MOCK_URL}/api/pay', headers={SCENARIO_HEADER: 'FAILURE'})

    assert response.status_code == 502
    assert response.json() == {'error': 'upstream failed'}


async def test_mock_scenario_invalid_header_falls_back_to_success(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/pay', status_code=200, response_body={'ok': True})
    await create_endpoint(
        method='GET',
        path='/api/pay',
        status_code=502,
        response_body={'error': 'upstream failed'},
        scenario='FAILURE',
    )

    response = await client.get(f'{MOCK_URL}/api/pay', headers={SCENARIO_HEADER: 'WHATEVER'})

    assert response.status_code == 200
    assert response.json() == {'ok': True}


async def test_project_mock_returns_configured_response(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Mocked')
    await create_endpoint(
        project_id=project['id'],
        method='GET',
        path='/api/projects-data',
        status_code=200,
        response_body={'scope': 'project'},
    )

    response = await client.get(f"{MOCK_URL}/projects/{project['id']}/api/projects-data")

    assert response.status_code == 200
    assert response.json() == {'scope': 'project'}


async def test_project_mock_does_not_leak_global_endpoint(client: AsyncClient, create_project, create_endpoint):
    project = await create_project('Isolated')
    await create_endpoint(method='GET', path='/api/global-only')

    response = await client.get(f"{MOCK_URL}/projects/{project['id']}/api/global-only")

    assert response.status_code == 404


async def test_project_mock_unknown_project(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/global-only')

    response = await client.get(f'{MOCK_URL}/projects/999999/api/global-only')

    assert response.status_code == 404


async def test_project_mock_does_not_leak_other_project(client: AsyncClient, create_project, create_endpoint):
    owner = await create_project('Owner')
    stranger = await create_project('Stranger')
    await create_endpoint(
        project_id=owner['id'],
        method='GET',
        path='/api/private',
        status_code=200,
    )

    response = await client.get(f"{MOCK_URL}/projects/{stranger['id']}/api/private")

    assert response.status_code == 404
