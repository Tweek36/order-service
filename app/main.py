"""Главный файл приложения FastAPI."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.infrastructure.database.session import close_db, init_db
from app.infrastructure.logging.config import configure_logging
from app.infrastructure.logging.middleware import RequestLoggingMiddleware
from app.presentation.api.v1 import orders
from app.settings import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager для startup/shutdown."""
    # Startup
    configure_logging(settings.LOG_LEVEL)
    await logger.ainfo("application_starting", service=settings.SERVICE_NAME)

    try:
        await init_db()
        await logger.ainfo("database_initialized")
    except Exception as e:
        await logger.aerror("database_init_failed", error=str(e))

    yield

    # Shutdown
    await logger.ainfo("application_shutting_down")
    await close_db()


app = FastAPI(
    title="Order Service",
    description="API для управления заказами",
    version="1.0.0",
    lifespan=lifespan,
)

# Добавляем middleware для логирования
app.add_middleware(RequestLoggingMiddleware)

# Подключаем роутеры
app.include_router(orders.router)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy"}
