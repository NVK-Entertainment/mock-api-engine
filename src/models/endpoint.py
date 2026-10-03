# Database dependencies
from src.database.db import Base
# SQL dependencies
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    )
# Typing dependencies
from sqlalchemy import (
    Integer,
    String,
    Enum,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
    )
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any
# HTTP-methods storage class
from src.models.helpers.methods import HttpMethods
from src.models.helpers.time_stamps import TimeStampMixin
from src.models.helpers.handle_scenario import HandleScenario


# Endpoints table
class Endpoint(TimeStampMixin, Base):
    __tablename__ = "endpoints"

    # Record id
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    project_id: Mapped[int] = mapped_column(
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

    # Table constraints
    __table_args__ = (
        # Table fields limiter
        CheckConstraint(
            "status_code >= 100 AND status_code <= 599",
            name="check_status_code_range"
        ),
        # Sequence of unique fileds in one row
        UniqueConstraint(
            'project_id', 
            'method', 
            'scenario', 
            'path',
            name='uq_endpoint_project_method_scenario_path'
        )
    )
