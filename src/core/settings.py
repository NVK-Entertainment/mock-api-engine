# Pydantic dependencies
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings
# Context dependencies
from core.dependencies import BASE_DIR


# Settings configuration class
class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        env_file_encoding="UTF-8",
    )

    # Database configuration
    db_user: str = "user"
    db_password: str = "password"
    db_host: str = "database"
    db_port: int = 5432
    db_name: str = "pstg"
    db_driver: str = "postgresql+psycopg"


# Settings object instance
settings = Settings()