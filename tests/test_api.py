# Tests
import pytest

# HTTP requests
from httpx import (
    AsyncClient, 
    ASGITransport
)
#from asgi_lifespan import LifespanManager

# FastAPI app object
from src.main import app


# GET /
async def test_healthcheck(client: AsyncClient):
    response = await client.get(url="/")
    
    assert response.status_code == 200
    assert response.json() == {'Healthcheck':'passed!'}

# GET /endpoints
#async def test_get_endpoints(client: AsyncClient):
#    response = await client.get(url="/endpoints")