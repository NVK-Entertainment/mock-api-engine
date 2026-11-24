# Services
from src.services.endpoint_service import EndpointService
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


class EndpointExportService:
    def __init__(
            self, 
            session: AsyncSession, 
            endpoint_service: EndpointService
        ):
        self.session = session
        self.endpoint_service = endpoint_service

    # Export specific endpoint by it's id
    async def export_endpoint_by_id(self, id: int):
        # Endpoint entity to export
        endpoint = await self.endpoint_service.get_endpoint_by_id(id)
        # Export-ready data
        export_data = EndpointExport(
            project_name = endpoint.project.name if endpoint.project else None,
            method = endpoint.method,
            path = endpoint.path,
            status_code = endpoint.status_code,
            scenario = endpoint.scenario,
            response_headers = endpoint.response_headers,
            response_body = endpoint.response_body,
            is_active = endpoint.is_active
        )
        # File ready entity
        document = FileExport(
            version=1,
            type=ExportEntityType.ENDPOINT,
            exported_at=datetime.now(timezone.utc),
            projects=(
                [ProjectExport(name=endpoint.project.name)]
                if endpoint.project else []
            ),
            endpoints=[export_data]
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
                "Content-Disposition": f'attachment; filename="endpoint:{str(uuid4())}.json"'
            },
        )
