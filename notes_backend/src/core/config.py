from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings sourced from environment variables.
    """

    # Database
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=3306, description="Database port")
    DB_NAME: str = Field(default="notes_db", description="Database name")
    DB_USER: str = Field(default="root", description="Database user")
    DB_PASSWORD: str = Field(default="", description="Database password")

    # Security / JWT
    JWT_SECRET: str = Field(default="CHANGE_ME", description="JWT secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="JWT expiration minutes")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    # CORS
    FRONTEND_ORIGIN: str = Field(default="*", description="Allowed frontend origin for CORS")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of Settings.
    """
    return Settings()
