# SQL mapping dependencies
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
)
from sqlalchemy import (
        DateTime, 
        func,
)
# Typing dependencies
from datetime import datetime


# Timestamp fields mixin helper class
class TimeStampMixin:
    # Timestamps fields
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=True,
            onupdate=func.now(),
        )
