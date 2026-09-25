# Fastapi dependencies
from fastapi import FastAPI
from contextlib import asynccontextmanager
# Database dependencies
from database.db import engine


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

# Healthcheck
@app.get('/', include_in_schema=False)
def healthcheck() -> dict:
    return {'Healthcheck':'passed!'}
