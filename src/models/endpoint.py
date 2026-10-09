# Database dependencies
from src.database.db import Base
# SQL dependencies
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    relationship,
    )
# Typing dependencies
from sqlalchemy import (
    Integer,
    String,
    Enum,
    Boolean,
    Index,
    text,
    CheckConstraint,
    ForeignKey,
    )
from sqlalchemy.dialects.postgresql import JSONB
from typing import (
    Any,
    TYPE_CHECKING
    )
# HTTP-methods storage class
from src.models.helpers.methods import HttpMethods
from src.models.helpers.time_stamps import TimeStampMixin
from src.models.helpers.handle_scenario import HandleScenario
# Models
if TYPE_CHECKING:
    from src.models.project import Project


# Endpoints table
class Endpoint(TimeStampMixin, Base):
    __tablename__ = "endpoints"

    # Record id
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    project_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('projects.id'),
        nullable=True,
    )
    # HTTP-methods
    method: Mapped[HttpMethods] = mapped_column(
        Enum(HttpMethods),
        nullable=False,
    )
    # Handle path
    path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    # Handle status code
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    # Handle scenario ('failure'/'success'/etc)
    scenario: Mapped[HandleScenario] = mapped_column(
        Enum(HandleScenario),
        nullable=False,
        default=HandleScenario.SUCCESS
    )
    # Handle header
    response_headers: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )
    # Handle response body
    response_body: Mapped[Any] = mapped_column(
        JSONB,
        nullable=True,
    )
    # Handle active status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    # Handle's project link (delete handles on project's deletion)
    project: Mapped['Project'] = relationship(
        back_populates='handles'
    )

    # Table constraints
    __table_args__ = (
        # status_code field limiter (validation)
        CheckConstraint(
            "status_code >= 100 AND status_code <= 599",
            name="check_status_code_range"
        ),
        # Partial indexes (uniqueness)
        Index(
            "uq_project_endpoint_route",
            "project_id",
            "method",
            "scenario",
            "path",
            unique=True,
            postgresql_where=text("project_id IS NOT NULL"),
        ),
        Index(
            "uq_global_endpoint_route",
            "method",
            "scenario",
            "path",
            unique=True,
            postgresql_where=text("project_id IS NULL"),
        ),
    )
