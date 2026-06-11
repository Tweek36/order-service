"""HTTP клиент для Payments Service."""

from decimal import Decimal
from uuid import UUID

import structlog

from app.application.dto.payments_dto import PaymentResponse
from app.infrastructure.clients.base_client import BaseHTTPClient
from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class PaymentsClient(BaseHTTPClient):
    """Клиент для взаимодействия с Payments Service."""

    def __init__(self):
        super().__init__(settings.PAYMENTS_SERVICE_URL, settings.API_TOKEN)

    async def create_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        callback_url: str,
        idempotency_key: str,
    ) -> PaymentResponse:
        """Создать платеж.

        Args:
            order_id: ID заказа
            amount: Сумма платежа
            callback_url: URL для callback
            idempotency_key: Ключ идемпотентности

        Returns:
            Информация о созданном платеже
        """
        payload = {
            "order_id": str(order_id),
            "amount": str(amount),
            "callback_url": callback_url,
            "idempotency_key": idempotency_key,
        }

        try:
            data = await self._post("/api/payments", payload)

            await logger.ainfo(
                "payment_created",
                payment_id=data["id"],
                order_id=str(order_id),
                amount=str(amount),
                status=data["status"],
            )

            return PaymentResponse(
                id=UUID(data["id"]),
                user_id=data["user_id"],
                order_id=UUID(data["order_id"]),
                amount=Decimal(data["amount"]),
                status=data["status"],
                idempotency_key=data["idempotency_key"],
            )
        except Exception as e:
            await logger.aerror(
                "payment_creation_failed",
                order_id=str(order_id),
                amount=str(amount),
                error=str(e),
            )
            raise
