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
    )

# HTTP-methods storage class
from models.methods import Methods


# Endpoints table
class Endpoint(Base):
    __tablename__ = "endpoints"

    project_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,   
    )
    # HTTP-methods
    method: Mapped[str] = mapped_column(
        Enum(Methods),
        primary_key=True,
        default=Methods.GET
    )
    # Handle path
    path: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )
    status_code: Mapped[str] = mapped_column(
        nullable=False,
    )
    response_headers: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

