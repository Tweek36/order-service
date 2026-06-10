"""DTO для callback от Payments Service."""

from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCallbackDTO(BaseModel):
    """DTO для callback от Payments Service."""

    payment_id: UUID = Field(..., description="ID платежа")
    order_id: UUID = Field(..., description="ID заказа")
    status: str = Field(..., description="Статус платежа (succeeded/failed)")
    amount: str = Field(..., description="Сумма платежа")
    error_message: str | None = Field(None, description="Сообщение об ошибке")
