from typing import Literal, Optional
from pydantic import computed_field, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Zentrale Konfiguration aus Umgebungsvariablen und .env-Datei."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "WeMood Backend"
    ENVIRONMENT: Literal["dev", "test", "prod"] = "dev"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "wemood_db"

    MISTRAL_API_KEY: str
    ADMIN_API_KEY: Optional[str] = None

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 Tag

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Baut die async PostgreSQL-Connection-URI aus den Einzelwerten zusammen."""
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings()