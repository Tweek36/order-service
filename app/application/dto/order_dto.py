"""DTO для заказов."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import OrderStatus


@dataclass
class CreateOrderDTO:
    """DTO для создания заказа."""

    user_id: str
    item_id: UUID
    quantity: int
    idempotency_key: str


@dataclass
class OrderDTO:
    """DTO заказа для ответа."""

    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
