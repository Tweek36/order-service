"""Модель заказа."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import OrderStatus


@dataclass
class Order:
    """Доменная модель заказа."""

    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    def can_be_cancelled(self) -> bool:
        """Проверить, можно ли отменить заказ."""
        return self.status in (OrderStatus.NEW, OrderStatus.PAID)

    def mark_as_paid(self) -> None:
        """Отметить заказ как оплаченный."""
        if self.status != OrderStatus.NEW:
            raise ValueError(f"Cannot mark order as paid from status {self.status}")
        self.status = OrderStatus.PAID
        self.updated_at = datetime.utcnow()

    def mark_as_shipped(self) -> None:
        """Отметить заказ как отправленный."""
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Cannot mark order as shipped from status {self.status}")
        self.status = OrderStatus.SHIPPED
        self.updated_at = datetime.utcnow()

    def mark_as_cancelled(self) -> None:
        """Отметить заказ как отмененный."""
        if not self.can_be_cancelled():
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
