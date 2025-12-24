from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Manager API"
    # DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://myuser:password@localhost/mydb"

    # Security
    SECRET_KEY: str = "your-super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "<http://localhost:3000>",
        "<https://fastapi-client.govindkulkarni.me>"
    ]

    # Redis
    REDIS_URL: str = "redis://localhost:6379"


    class Config:
        env_file = ".env"

settings = Settings()
