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
    response = await client.get(url="/healthcheck")
    
    assert response.status_code == 200
    assert response.json() == {'Healthcheck':'passed!'}

