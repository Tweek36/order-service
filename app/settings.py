"""Настройки приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения Order Service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # PostgreSQL settings
    POSTGRES_HOST: str = "postgres-postgresql.postgres.svc"
    POSTGRES_PORT: int = 5432
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE_NAME: str = "student_Tweek36-order-service-postgres"
    POSTGRES_CONNECTION_STRING: str | None = None

    @property
    def database_url(self) -> str:
        """Получить URL для подключения к базе данных."""
        if self.POSTGRES_CONNECTION_STRING:
            return self.POSTGRES_CONNECTION_STRING
        return (
            f"postgresql://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}"
        )


def get_settings() -> Settings:
    """Получить экземпляр настроек."""
    return Settings()
