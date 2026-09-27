# Database dependencies
#from database.db import Base
# SQL dependencies
#from sqlalchemy.orm import (
#    Mapped, 
#    mapped_column,
#    )
# Typing dependencies
#from sqlalchemy import (
#    Integer,
#    String,
#    Enum,
#    JSON,
#    DateTime,
#    Boolean,
#    func,
#    UniqueConstraint,
#    CheckConstraint,
#    ForeignKey,
#    )
#from typing import Any
#from datetime import datetime
# HTTP-methods storage class
#from models.helpers.methods import Methods
#from models.helpers.time_stamps import TimeStampMixin
#
#
# ============= TEMPORALY FROZEN =================
# Project members pivot table
#class ProjectMembers(TimeStampMixin, Base):
#    __tablename__ = 'project_members'
#
#    project_id: Mapped[int] = mapped_column(
#        Integer,
#        ForeignKey('projects.id'),
#    )
#