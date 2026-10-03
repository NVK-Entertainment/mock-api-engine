# Fastapi dependencies
from fastapi import FastAPI, status
from contextlib import asynccontextmanager
# Database dependencies
from src.database.db import engine
# API routers
from src.api.v1.endpoint_router import router as endpoint_router
# Models
import src.models


# App's lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Action on app shutting down
    print("Shutting down...") 
    engine.dispose()

# App object
app = FastAPI(
    lifespan=lifespan
    )

# API routers connection
app.include_router(endpoint_router)

# Healthcheck
@app.get(
    '/', 
    include_in_schema=False, 
    status_code=status.HTTP_200_OK,
)
def healthcheck() -> dict:
    return {'Healthcheck':'passed!'}
