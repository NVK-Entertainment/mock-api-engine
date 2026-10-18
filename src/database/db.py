# SQL dependencies
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, 
    AsyncSession,
    create_async_engine
    )
# SQL metadata dependencies
from sqlalchemy.orm import DeclarativeBase
# Settings configuration
from src.core.config import settings
# Annotation
from typing import AsyncGenerator


# Database connection URL
DB_URL = (
    f"{settings.db_driver}://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

# Database connection engine
engine = create_async_engine(
    url=DB_URL,
    pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
    )

# Base metaclass
class Base(DeclarativeBase):
    pass

# Database session generator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
