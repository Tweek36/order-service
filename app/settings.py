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
    POSTGRES_USERNAME: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DATABASE_NAME: str = "student_Tweek36-order-service-postgres"
    POSTGRES_CONNECTION_STRING: str | None = None

    # Capashino settings
    CAPASHINO_BASE_URL: str = "https://capashino.dev-2.python-labs.ru"
    X_API_KEY: str = "test_api_key"

    @property
    def API_TOKEN(self) -> str:
        """Alias for X_API_KEY for backward compatibility."""
        return self.X_API_KEY

    @property
    def CATALOG_SERVICE_URL(self) -> str:
        """URL для Catalog Service."""
        return self.CAPASHINO_BASE_URL

    @property
    def PAYMENTS_SERVICE_URL(self) -> str:
        """URL для Payments Service."""
        return self.CAPASHINO_BASE_URL

    @property
    def NOTIFICATIONS_SERVICE_URL(self) -> str:
        """URL для Notifications Service."""
        return "http://student-system-capashino-web.student-system-capashino.svc:8000"

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka.kafka.svc.cluster.local:9092"
    KAFKA_ORDER_EVENTS_TOPIC: str = "student_system-order.events"
    KAFKA_SHIPMENT_EVENTS_TOPIC: str = "student_system-shipment.events"
    KAFKA_CONSUMER_GROUP: str = "order-service-group"

    # Service settings
    SERVICE_NAME: str = "student-tweek36-order-service-web"
    SERVICE_NAMESPACE: str = "student-tweek36-order-service"
    SERVICE_PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        """Получить URL для подключения к базе данных."""
        if self.POSTGRES_CONNECTION_STRING:
            # Заменяем postgres:// на postgresql+asyncpg:// для asyncpg драйвера
            connection_string = self.POSTGRES_CONNECTION_STRING
            if connection_string.startswith("postgres://"):
                connection_string = connection_string.replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )
            return connection_string
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}"
        )

    @property
    def callback_url(self) -> str:
        """Получить URL для callback от Payment Service."""
        return (
            f"http://{self.SERVICE_NAME}.{self.SERVICE_NAMESPACE}.svc:"
            f"{self.SERVICE_PORT}/api/orders/payment-callback"
        )


def get_settings() -> Settings:
    """Получить экземпляр настроек."""
    return Settings()
