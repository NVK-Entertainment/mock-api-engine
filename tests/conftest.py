# Tests
import pytest
# Annotations
from typing import AsyncIterator
# HTTP requests
from httpx import (
    AsyncClient, 
    ASGITransport
)
# Database
from sqlalchemy import text
from src.database.db import engine
# FastAPI app object
from src.main import app


# API urls constants
PROJECTS_URL = '/api/v1/projects'
ENDPOINTS_URL = '/api/v1/management/endpoints'


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(autouse=True)
async def clean_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE projects, endpoints CASCADE"))
    yield


@pytest.fixture
async def create_project(client: AsyncClient) -> AsyncIterator:
    async def _create_project(name: str) -> dict:
        response = await client.post(PROJECTS_URL, json={'name': name})
        assert response.status_code == 201, response.text
        return response.json()
    yield _create_project


@pytest.fixture
async def create_endpoint(client: AsyncClient) -> AsyncIterator:
    async def _create_endpoint(**overrides) -> dict:
        payload = {
            'method': 'GET',
            'path': '/test',
            'status_code': 200,
            'response_body': {'ok': True},
        }
        payload.update(overrides)
        response = await client.post(ENDPOINTS_URL, json=payload)
        assert response.status_code == 201, response.text
        return response.json()
    yield _create_endpoint
