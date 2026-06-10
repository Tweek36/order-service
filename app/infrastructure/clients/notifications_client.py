"""HTTP клиент для Notifications Service."""

from uuid import UUID

import httpx
import structlog

from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class NotificationsClient:
    """Клиент для взаимодействия с Notifications Service."""

    def __init__(self):
        self.base_url = settings.NOTIFICATIONS_SERVICE_URL
        self.api_token = settings.API_TOKEN
        self.timeout = 10.0

    async def send_notification(
        self,
        message: str,
        reference_id: UUID,
        idempotency_key: str,
    ) -> dict | None:
        """Отправить уведомление.

        Args:
            message: Текст уведомления
            reference_id: ID заказа (reference)
            idempotency_key: Ключ идемпотентности

        Returns:
            Данные созданного уведомления или None в случае ошибки
        """
        url = f"{self.base_url}/api/notifications"
        headers = {"X-API-Key": self.api_token}
        payload = {
            "message": message,
            "reference_id": str(reference_id),
            "idempotency_key": idempotency_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                notification_data = response.json()
                await logger.ainfo(
                    "notification_sent",
                    notification_id=notification_data.get("id"),
                    reference_id=str(reference_id),
                )
                return notification_data

        except httpx.HTTPStatusError as e:
            await logger.aerror(
                "notification_send_failed",
                status_code=e.response.status_code,
                error=str(e),
                reference_id=str(reference_id),
            )
            return None
        except Exception as e:
            await logger.aerror(
                "notification_send_error",
                error=str(e),
                reference_id=str(reference_id),
            )
            return None
