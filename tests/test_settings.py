"""Тесты для настроек приложения."""

import pytest
from pydantic import ValidationError

from app.settings import Settings


def test_settings_with_all_parameters():
    """Тест создания настроек со всеми параметрами."""
    settings = Settings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USERNAME="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_DATABASE_NAME="testdb",
    )

    assert settings.POSTGRES_HOST == "localhost"
    assert settings.POSTGRES_PORT == 5432
    assert settings.POSTGRES_USERNAME == "testuser"
    assert settings.POSTGRES_PASSWORD == "testpass"
    assert settings.POSTGRES_DATABASE_NAME == "testdb"


def test_database_url_construction():
    """Тест формирования URL для подключения к базе данных."""
    settings = Settings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USERNAME="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_DATABASE_NAME="testdb",
    )

    expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
    assert settings.database_url == expected_url


def test_connection_string_override():
    """Тест использования готовой строки подключения."""
    custom_connection = "postgresql://custom:pass@custom.host:5433/customdb"
    settings = Settings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_USERNAME="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_DATABASE_NAME="testdb",
        POSTGRES_CONNECTION_STRING=custom_connection,
    )

    assert settings.database_url == custom_connection


def test_default_values():
    """Тест значений по умолчанию."""
    settings = Settings(
        POSTGRES_USERNAME="testuser",
        POSTGRES_PASSWORD="testpass",
    )

    assert settings.POSTGRES_HOST == "postgres-postgresql.postgres.svc"
    assert settings.POSTGRES_PORT == 5432
    assert settings.POSTGRES_DATABASE_NAME == "student_Tweek36-order-service-postgres"


def test_missing_required_fields():
    """Тест ошибки при отсутствии обязательных полей."""
    with pytest.raises(ValidationError) as exc_info:
        Settings()

    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}

    assert "POSTGRES_USERNAME" in error_fields
    assert "POSTGRES_PASSWORD" in error_fields
