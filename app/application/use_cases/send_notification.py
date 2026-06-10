"""Use case для отправки уведомлений."""

from uuid import UUID

import structlog

from app.infrastructure.clients.notifications_client import NotificationsClient

logger = structlog.get_logger(__name__)


class SendNotificationUseCase:
    """Use case для отправки уведомлений пользователям."""

    def __init__(self, notifications_client: NotificationsClient):
        self.notifications_client = notifications_client

    async def execute(
        self,
        order_id: UUID,
        message: str,
        idempotency_key: str,
    ) -> None:
        """Отправить уведомление.

        Args:
            order_id: ID заказа
            message: Текст уведомления
            idempotency_key: Ключ идемпотентности
        """
        try:
            result = await self.notifications_client.send_notification(
                message=message,
                reference_id=order_id,
                idempotency_key=idempotency_key,
            )

            if result:
                await logger.ainfo(
                    "notification_sent_successfully",
                    order_id=str(order_id),
                    notification_id=result.get("id"),
                )
            else:
                await logger.awarning(
                    "notification_send_failed_but_not_blocking",
                    order_id=str(order_id),
                )
        except Exception as e:
            # Не блокируем основной процесс, только логируем
            await logger.aerror(
                "notification_send_error",
                order_id=str(order_id),
                error=str(e),
            )
