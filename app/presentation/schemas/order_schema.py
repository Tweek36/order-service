"""Схемы для заказов."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import OrderStatus


class CreateOrderRequest(BaseModel):
    """Запрос на создание заказа."""

    user_id: str = Field(..., description="ID пользователя")
    item_id: UUID = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество")
    idempotency_key: str = Field(..., description="Ключ идемпотентности")


class OrderResponse(BaseModel):
    """Ответ с информацией о заказе."""

    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
