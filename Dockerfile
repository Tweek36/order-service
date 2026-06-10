# Multi-stage build для оптимизации размера образа
FROM python:3.13-slim AS builder

# Установка зависимостей для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.13-slim

# Устанавливаем runtime зависимости для PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создаем системную группу и пользователя
RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

# Копируем установленные зависимости из builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код приложения и конфигурацию alembic
COPY --chown=appuser:appuser app /app/app
COPY --chown=appuser:appuser alembic /app/alembic
COPY --chown=appuser:appuser alembic.ini /app/alembic.ini

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
