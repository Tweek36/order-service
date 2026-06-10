"""Схемы для заказов."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import OrderStatus


class CreateOrderRequest(BaseModel):
    """Запрос на создание заказа."""

    user_id: str = Field(..., description="ID пользователя")
    item_id: UUID | None = Field(None, description="ID товара")
    item_name: str | None = Field(None, description="Название товара")
    quantity: int = Field(..., gt=0, description="Количество")
    idempotency_key: str = Field(..., description="Ключ идемпотентности")

    def model_post_init(self, __context) -> None:
        """Валидация: должен быть указан либо item_id, либо item_name."""
        if not self.item_id and not self.item_name:
            raise ValueError("Either item_id or item_name must be provided")


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
