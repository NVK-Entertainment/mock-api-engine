# SQL dependencies
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker, 
    Session
    )
# SQL metadata dependencies
from sqlalchemy.orm import DeclarativeBase
# Settings configuration
from src.core.settings import settings


# Database connection URL
DB_URL = (
    f"{settings.db_driver}://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

# Database connection engine
engine = create_engine(
    url=DB_URL,
    pool_pre_ping=True,
    )

session_local = sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

# Base metaclass
class Base(DeclarativeBase):
    pass

# Database session generator
def get_session():
    with session_local() as session:
        yield session
