# Database dependencies
from src.database.db import Base
# SQL dependencies
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    relationship
    )
# Typing dependencies
from sqlalchemy import (
    Integer,
    String,
    )
# HTTP-methods storage class
from src.models.helpers.time_stamps import TimeStampMixin
# Models
from src.models.endpoint import Endpoint


# Project object ORM model
class Project(TimeStampMixin, Base):
    __tablename__ = 'projects'

    # Project id
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    # Project name
    name: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        unique=True,
    )

    # List of api handles that contains in the project
    handles: Mapped[list['Endpoint']]= relationship()
    
    # ========== TEMPORALY FROZEN =========
    #members: Mapped[list['User']] = relationship(
    #    back_populates='projects'
    #)
