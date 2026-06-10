"""Перечисления для domain слоя."""

from enum import Enum


class OrderStatus(str, Enum):
    """Статусы заказа."""

    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"
