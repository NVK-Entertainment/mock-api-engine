# HTTP requests
from httpx import AsyncClient
# Url constants
from tests.conftest import ENDPOINTS_URL


async def test_create_global_endpoint(client: AsyncClient):
    payload = {
        'method': 'GET',
        'path': '/api/users',
        'status_code': 200,
        'response_body': {'id': 1},
    }

    response = await client.post(ENDPOINTS_URL, json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data['project_id'] is None
    assert data['method'] == 'GET'
    assert data['path'] == '/api/users'
    assert data['status_code'] == 200
    assert data['response_body'] == {'id': 1}
    assert data['response_headers'] == {}
    assert data['scenario'] == 'SUCCESS'
    assert data['is_active'] is True
    assert data['created_at'] is not None
    assert data['updated_at'] is None


async def test_create_endpoint_in_project(client: AsyncClient, create_project):
    project = await create_project('Scoped')

    response = await client.post(
        ENDPOINTS_URL,
        json={
            'project_id': project['id'],
            'method': 'POST',
            'path': '/api/orders',
            'status_code': 201,
            'response_body': {'order_id': 42},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data['project_id'] == project['id']
    assert data['method'] == 'POST'
    assert data['status_code'] == 201


async def test_create_endpoint_duplicate_route(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/dup', scenario='SUCCESS')

    response = await client.post(
        ENDPOINTS_URL,
        json={
            'method': 'GET',
            'path': '/api/dup',
            'status_code': 200,
            'scenario': 'SUCCESS',
        },
    )

    assert response.status_code == 409


async def test_create_endpoint_same_route_different_scenario(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/pay', scenario='SUCCESS')

    response = await client.post(
        ENDPOINTS_URL,
        json={
            'method': 'GET',
            'path': '/api/pay',
            'status_code': 502,
            'scenario': 'FAILURE',
        },
    )

    assert response.status_code == 201
    assert response.json()['scenario'] == 'FAILURE'


async def test_create_endpoint_same_route_different_project(client: AsyncClient, create_project):
    first = await create_project('First')
    second = await create_project('Second')
    await client.post(
        ENDPOINTS_URL,
        json={
            'project_id': first['id'],
            'method': 'GET',
            'path': '/api/shared',
            'status_code': 200,
        },
    )

    response = await client.post(
        ENDPOINTS_URL,
        json={
            'project_id': second['id'],
            'method': 'GET',
            'path': '/api/shared',
            'status_code': 200,
        },
    )

    assert response.status_code == 201
    assert response.json()['project_id'] == second['id']


async def test_create_endpoint_unknown_project(client: AsyncClient):
    response = await client.post(
        ENDPOINTS_URL,
        json={
            'project_id': 999999,
            'method': 'GET',
            'path': '/api/orphan',
            'status_code': 200,
        },
    )

    assert response.status_code == 409


async def test_create_endpoint_invalid_status_code(client: AsyncClient):
    for code in (99, 600):
        response = await client.post(
            ENDPOINTS_URL,
            json={
                'method': 'GET',
                'path': '/api/invalid',
                'status_code': code,
            },
        )
        assert response.status_code == 422


async def test_create_endpoint_path_normalization(client: AsyncClient):
    response = await client.post(
        ENDPOINTS_URL,
        json={
            'method': 'GET',
            'path': 'api/users/',
            'status_code': 200,
        },
    )

    assert response.status_code == 201
    assert response.json()['path'] == '/api/users'


async def test_create_endpoint_normalized_path_is_unique(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='api/users/')

    response = await client.post(
        ENDPOINTS_URL,
        json={
            'method': 'GET',
            'path': '/api/users',
            'status_code': 200,
        },
    )

    assert response.status_code == 409


async def test_get_endpoint(client: AsyncClient, create_endpoint):
    created = await create_endpoint(path='/api/gettable')

    response = await client.get(f"{ENDPOINTS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_endpoint_not_found(client: AsyncClient):
    response = await client.get(f'{ENDPOINTS_URL}/999999')

    assert response.status_code == 404


async def test_get_all_endpoints(client: AsyncClient, create_endpoint):
    first = await create_endpoint(path='/api/one')
    second = await create_endpoint(method='POST', path='/api/two')

    response = await client.get(ENDPOINTS_URL)

    assert response.status_code == 200
    ids = {e['id'] for e in response.json()}
    assert ids == {first['id'], second['id']}


async def test_update_endpoint(client: AsyncClient, create_endpoint):
    created = await create_endpoint(path='/api/updatable')

    response = await client.patch(
        f"{ENDPOINTS_URL}/{created['id']}",
        json={
            'status_code': 404,
            'response_body': {'error': 'gone'},
            'is_active': False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['status_code'] == 404
    assert data['response_body'] == {'error': 'gone'}
    assert data['is_active'] is False
    assert data['path'] == '/api/updatable'


async def test_update_endpoint_conflict(client: AsyncClient, create_endpoint):
    await create_endpoint(method='GET', path='/api/busy')
    created = await create_endpoint(method='GET', path='/api/free')

    response = await client.patch(
        f"{ENDPOINTS_URL}/{created['id']}",
        json={'path': '/api/busy'},
    )

    assert response.status_code == 409


async def test_update_endpoint_not_found(client: AsyncClient):
    response = await client.patch(f'{ENDPOINTS_URL}/999999', json={'path': '/api/any'})

    assert response.status_code == 404


async def test_delete_endpoint(client: AsyncClient, create_endpoint):
    created = await create_endpoint(path='/api/deletable')

    response = await client.delete(f"{ENDPOINTS_URL}/{created['id']}")

    assert response.status_code == 204
    assert (await client.get(f"{ENDPOINTS_URL}/{created['id']}")).status_code == 404


async def test_delete_endpoint_not_found(client: AsyncClient):
    response = await client.delete(f'{ENDPOINTS_URL}/999999')

    assert response.status_code == 404
