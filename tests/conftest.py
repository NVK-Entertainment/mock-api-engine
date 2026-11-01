# Tests
import pytest
# Annotations
from typing import AsyncIterator
# HTTP requests
from httpx import (
    AsyncClient, 
    ASGITransport
)
# FastAPI app object
from src.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
