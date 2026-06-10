"""Middleware для логирования HTTP запросов."""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования всех HTTP запросов."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием.

        Args:
            request: HTTP запрос
            call_next: Следующий обработчик в цепочке

        Returns:
            HTTP ответ
        """
        # Генерируем request_id для трейсинга
        request_id = str(uuid.uuid4())

        # Добавляем request_id в контекст
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        start_time = time.time()

        # Логируем входящий запрос
        await logger.ainfo(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)

            # Вычисляем время обработки
            duration = time.time() - start_time

            # Логируем успешный ответ
            await logger.ainfo(
                "request_completed",
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )

            # Добавляем request_id в заголовки ответа
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            duration = time.time() - start_time

            # Логируем ошибку
            await logger.aerror(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                duration_seconds=round(duration, 3),
                exc_info=True,
            )
            raise
