"""Доменные исключения."""


class DomainException(Exception):
    """Базовое исключение для domain слоя."""

    pass


class OrderNotFoundError(DomainException):
    """Заказ не найден."""

    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")


class InsufficientStockError(DomainException):
    """Недостаточное количество товара на складе."""

    def __init__(self, item_id: str, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for item {item_id}: "
            f"requested {requested}, available {available}"
        )


class DuplicateOrderError(DomainException):
    """Попытка создать дубликат заказа (нарушение идемпотентности)."""

    def __init__(self, idempotency_key: str, existing_order_id: str):
        self.idempotency_key = idempotency_key
        self.existing_order_id = existing_order_id
        super().__init__(
            f"Order with idempotency key {idempotency_key} "
            f"already exists (order_id: {existing_order_id})"
        )


class PaymentCreationError(DomainException):
    """Ошибка при создании платежа."""

    pass


class ItemNotFoundError(DomainException):
    """Товар не найден в каталоге."""

    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(f"Item with id {item_id} not found in catalog")
