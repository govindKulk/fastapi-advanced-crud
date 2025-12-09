from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # These default values will act as fallbacks if not environment variables are set.
    # .env -> explicit environment variables -> defaults this is the order of precedence.

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/taskmanager"

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Manager API"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    REDIS_URL: str = "redis://localhost:6379"

    # this inner config class tells pydantic to read from a .env file
    # this pattern is common for pydantic settings management
    class Config:
        env_file = ".env"


settings = Settings()