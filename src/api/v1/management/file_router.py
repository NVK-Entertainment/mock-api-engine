# FastAPI dependencies
from fastapi import (
    APIRouter, 
    Depends, 
    status
)
# Annotation
from typing import Annotated
# Services
from src.services.file_handlers.endpoint_export_service import EndpointExportService
from src.services.file_handlers.projects_export_service import ProjectExportService
# DI
from src.core.factories import get_endpoint_export_service
from src.core.factories import get_project_export_service


# File router
router = APIRouter(prefix='/api/v1/management')

@router.get(
    "endpoints/{endpoint_id}/export",
    status_code=status.HTTP_200_OK,
)
async def export_endpoint(
    endpoint_id: int, 
    service: Annotated[EndpointExportService, Depends(get_endpoint_export_service)]
    ):
    return await service.export_endpoint_by_id(endpoint_id)

@router.get(
    "/projects/{project_id}/export",
    status_code=status.HTTP_200_OK,
)
async def export_project(
    project_id: int,
    service: Annotated[ProjectExportService, Depends(get_project_export_service)]
):
    return await service.export_project_by_id(project_id)
