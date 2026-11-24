# Services
from src.services.endpoint_service import EndpointService
from src.services.project_service import ProjectService
# Schemas
from src.schemas.export_schemas.endpoint_export_schema import EndpointExport
from src.schemas.export_schemas.file_export import FileExport
from src.schemas.export_schemas.project_export_schema import ProjectExport
from src.models.helpers.export_entity_type import ExportEntityType

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from datetime import datetime, timezone
import json
from uuid import uuid4


class ProjectExportService:
    def __init__(
            self, 
            session: AsyncSession, 
            endpoint_service: EndpointService,
            project_service: ProjectService,
        ):
        self.session = session
        self.endpoint_service = endpoint_service
        self.project_service = project_service

    # Export specific project by it's id
    async def export_project_by_id(self, id: int):
        # Project entity to export
        project = await self.project_service.get_project_by_id(id)
        # Export-ready data
        export_data = ProjectExport(
            name = project.name,
        )
        # File ready entity
        document = FileExport(
            version=1,
            type=ExportEntityType.PROJECT,
            exported_at=datetime.now(timezone.utc),
            projects=([ProjectExport(name=project.name)]),
            endpoints=[EndpointExport(
                project_name=project.name, 
                method=endpoint.method,
                path=endpoint.path,
                status_code=endpoint.status_code,
                scenario=endpoint.scenario,
                response_headers=endpoint.response_headers,
                response_body=endpoint.response_body,
                is_active=endpoint.is_active,
            ) for endpoint in project.handles]
        )
        # Reponse content
        content = json.dumps(
            document.model_dump(mode='json'),
            ensure_ascii=False,
            indent=2,
        )
        
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="project:{str(uuid4())}.json"'
            },
        )
