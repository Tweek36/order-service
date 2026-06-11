"""DTO для Payments Service."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class PaymentResponse:
    """Ответ от Payments Service при создании платежа."""

    id: UUID
    user_id: str
    order_id: UUID
    amount: Decimal
    status: str
    idempotency_key: str
