# HTTP requests
from httpx import AsyncClient
# Url constants
from tests.conftest import PROJECTS_URL


async def test_create_project(client: AsyncClient):
    response = await client.post(PROJECTS_URL, json={'name': 'Test Project'})

    assert response.status_code == 201
    data = response.json()
    assert data['id'] > 0
    assert data['name'] == 'Test Project'


async def test_create_project_duplicate_name(client: AsyncClient):
    await client.post(PROJECTS_URL, json={'name': 'Duplicate'})

    response = await client.post(PROJECTS_URL, json={'name': 'Duplicate'})

    assert response.status_code == 409


async def test_create_project_name_too_long(client: AsyncClient):
    response = await client.post(PROJECTS_URL, json={'name': 'x' * 33})

    assert response.status_code == 422


async def test_create_project_empty_name(client: AsyncClient):
    response = await client.post(PROJECTS_URL, json={'name': ''})

    assert response.status_code == 422


async def test_get_project(client: AsyncClient, create_project):
    created = await create_project('Gettable')

    response = await client.get(f"{PROJECTS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_project_not_found(client: AsyncClient):
    response = await client.get(f'{PROJECTS_URL}/999999')

    assert response.status_code == 404


async def test_get_all_projects(client: AsyncClient, create_project):
    await create_project('Alpha')
    await create_project('Beta')

    response = await client.get(PROJECTS_URL)

    assert response.status_code == 200
    names = {p['name'] for p in response.json()}
    assert names == {'Alpha', 'Beta'}


async def test_update_project(client: AsyncClient, create_project):
    created = await create_project('Old')

    response = await client.patch(f"{PROJECTS_URL}/{created['id']}", json={'name': 'New'})

    assert response.status_code == 200
    assert response.json()['name'] == 'New'


async def test_update_project_to_existing_name(client: AsyncClient, create_project):
    await create_project('Taken')
    created = await create_project('Renamable')

    response = await client.patch(f"{PROJECTS_URL}/{created['id']}", json={'name': 'Taken'})

    assert response.status_code == 409


async def test_update_project_not_found(client: AsyncClient):
    response = await client.patch(f'{PROJECTS_URL}/999999', json={'name': 'New'})

    assert response.status_code == 404


async def test_delete_project(client: AsyncClient, create_project):
    created = await create_project('Deletable')

    response = await client.delete(f"{PROJECTS_URL}/{created['id']}")

    assert response.status_code == 204
    assert (await client.get(f"{PROJECTS_URL}/{created['id']}")).status_code == 404


async def test_delete_project_not_found(client: AsyncClient):
    response = await client.delete(f'{PROJECTS_URL}/999999')

    assert response.status_code == 404
