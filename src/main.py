# Fastapi dependencies
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
# Database dependencies
from src.database.db import engine
# API routers
from src.api.v1.management.endpoint_router import router as endpoint_router
from src.api.v1.management.project_router import router as project_router
from src.api.v1.runtime.mock_router import router as mock_router
from src.api.v1.workflows.workflow_router import router as workflow_router
from src.api.v1.ui.ui_router import router as ui_router
from src.api.v1.management.file_router import router as file_router
# Context dependencies
from src.core.dependencies import BASE_DIR
# Models (don't remove, imported for alembic context)
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

# App's CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers connection
app.include_router(endpoint_router, tags=['Endpoints Management'])
app.include_router(project_router, tags=['Projects Managements'])
app.include_router(mock_router, tags=['Mocks Responses'])
app.include_router(workflow_router, tags=['Workflows'])
app.include_router(ui_router)
app.include_router(file_router, tags=['Files'])

# Static files for the web UI (Bootstrap overrides and scripts)
app.mount('/static', StaticFiles(directory=BASE_DIR / 'src' / 'static'), name='static')

# Healthcheck
@app.get(
    '/healthcheck', 
    include_in_schema=False, 
    status_code=status.HTTP_200_OK,
)
def healthcheck() -> dict:
    return {'Healthcheck':'passed!'}
