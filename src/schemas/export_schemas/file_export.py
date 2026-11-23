from src.models.helpers.export_entity_type import ExportEntityType
from pydantic import (
    BaseModel, 
    ConfigDict,
    Field,
    model_validator
)
from typing import Literal
from datetime import datetime
from src.schemas.export_schemas.endpoint_export_schema import EndpointExport
from src.schemas.export_schemas.project_export_schema import ProjectExport


# File(Json) exporting schema 
class FileExport(BaseModel):
    model_config = ConfigDict(extra='forbid')

    version: Literal[1]
    type: ExportEntityType
    exported_at: datetime | None = None
    projects: list[ProjectExport] = Field(default_factory=list)
    endpoints: list[EndpointExport] = Field(default_factory=list)

    @model_validator(mode='after')
    def _check_type(self):
        if self.type is ExportEntityType.ENDPOINT and len(self.endpoints) != 1:
            raise ValueError("Exporting type 'endpoint' require exactly one endpoint entity")
        if self.type is ExportEntityType.GLOBAL and self.projects:
            raise ValueError("Exporting type 'global' mustn't contain projects entities")
        return self
