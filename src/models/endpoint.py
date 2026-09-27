# Database dependencies
from database.db import Base
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
    JSON,
    DATETIME,
    Boolean,
    func,
    UniqueConstraint,
    CheckConstraint,
    )
from typing import Any
from datetime import datetime
# HTTP-methods storage class
from models.methods import Methods


# Endpoints table
class Endpoint(Base):
    __tablename__ = "endpoints"

    # Record id
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    #project_id: Mapped[int] = mapped_column(
    #    Integer,
    #    nullable=False,
    #)
    # HTTP-methods
    method: Mapped[str] = mapped_column(
        Enum(Methods),
        nullable=False,
    )
    # Handle path
    path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    # Handle status code
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    # Handle header
    response_headers: Mapped[Any] = mapped_column(
        JSON,
        nullable=False,
    )
    # Handle response body
    response_body: Mapped[Any] = mapped_column(
        JSON,
        nullable=True,
    )
    # Handle active status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    # Timestamps fields
    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint("status_code >= 100 AND status_code <= 599"),
        UniqueConstraint('project_id', 'method', 'status_code', 'path')
    )