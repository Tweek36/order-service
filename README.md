# Order Service

Микросервис для управления заказами в системе Capashino.

## Архитектура

Проект следует принципам **Clean Architecture**:

```
app/
├── domain/              # Бизнес-логика и модели
├── application/         # Use cases и DTO
├── infrastructure/      # Внешние зависимости (БД, HTTP, Kafka)
└── presentation/        # API endpoints
```

## Технологии

- **FastAPI** - async web framework
- **SQLAlchemy 2.0** - async ORM
- **Alembic** - миграции БД
- **PostgreSQL** - база данных
- **Kafka** - event streaming
- **structlog** - структурированное логирование
- **httpx** - async HTTP клиент

## API Endpoints

### Создать заказ
```http
POST /api/orders
Content-Type: application/json

{
  "user_id": "user-123",
  "item_id": "uuid-товара",
  "quantity": 10,
  "idempotency_key": "unique-key"
}
```

**Ответ (201 Created):**
```json
{
  "id": "order-uuid",
  "user_id": "user-123",
  "item_id": "item-uuid",
  "quantity": 10,
  "status": "NEW",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Получить заказ
```http
GET /api/orders/{order_id}
```

**Ответ (200 OK):**
```json
{
  "id": "order-uuid",
  "user_id": "user-123",
  "item_id": "item-uuid",
  "quantity": 10,
  "status": "NEW",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Health Check
```http
GET /health
```

## Статусы заказа

- **NEW** - заказ создан
- **PAID** - платеж успешен
- **SHIPPED** - заказ отправлен
- **CANCELLED** - заказ отменен

## Интеграции

### Catalog Service
Проверка наличия товаров и их количества.

### Payments Service
Обработка платежей с асинхронными callbacks.

### Shipping Service (через Kafka)
- Публикация: `order.paid` событие
- Подписка: `order.shipped`, `order.cancelled` события

### Notifications Service
Отправка уведомлений при изменении статуса заказа.

## Паттерны

- **Repository Pattern** - абстракция доступа к данным
- **Unit of Work** - управление транзакциями
- **Outbox Pattern** - надежная публикация событий в Kafka
- **Inbox Pattern** - идемпотентная обработка входящих событий
- **Dependency Injection** - через FastAPI Depends

## Логирование

Структурированные JSON логи с помощью `structlog`:

```json
{
  "event": "request_completed",
  "request_id": "uuid",
  "method": "POST",
  "path": "/api/orders",
  "status_code": 201,
  "duration_seconds": 0.123,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Разработка

### Создание новой миграции

```bash
alembic revision --autogenerate -m "description"
```

### Запуск тестов

```bash
pytest
```

### Проверка кода

```bash
ruff check .
mypy app
```
