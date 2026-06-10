"""Use case для обработки событий от Shipping Service."""

import structlog

from app.application.dto.shipping_event_dto import (
    OrderCancelledEventDTO,
    OrderShippedEventDTO,
)
from app.domain.exceptions import OrderNotFoundError
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.clients.notifications_client import NotificationsClient
from app.infrastructure.database.repositories.inbox_repository import InboxRepository

logger = structlog.get_logger(__name__)


class ProcessShippingEventUseCase:
    """Use case для обработки событий от Shipping Service."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        inbox_repository: InboxRepository,
        notifications_client: NotificationsClient,
    ):
        self.order_repository = order_repository
        self.inbox_repository = inbox_repository
        self.notifications_client = notifications_client

    async def process_order_shipped(
        self,
        event: OrderShippedEventDTO,
        idempotency_key: str,
    ) -> None:
        """Обработать событие ORDER.SHIPPED.

        Args:
            event: Данные события
            idempotency_key: Ключ идемпотентности

        Raises:
            OrderNotFoundError: Заказ не найден
        """
        await logger.ainfo(
            "processing_order_shipped_event",
            order_id=str(event.order_id),
            shipment_id=str(event.shipment_id),
        )

        # Проверяем, не обработали ли мы уже это событие (Inbox паттерн)
        is_new = await self.inbox_repository.save_event(
            event_id=idempotency_key,
            event_type=event.event_type,
            payload=event.model_dump(mode="json"),
        )

        if not is_new:
            await logger.ainfo(
                "order_shipped_event_already_processed",
                order_id=str(event.order_id),
                idempotency_key=idempotency_key,
            )
            return

        # Получаем заказ
        order = await self.order_repository.get_by_id(event.order_id)
        if not order:
            await logger.aerror(
                "order_not_found_for_shipping_event",
                order_id=str(event.order_id),
            )
            raise OrderNotFoundError(str(event.order_id))

        # Обновляем статус заказа
        try:
            order.mark_as_shipped()
            await self.order_repository.update(order)

            # Отмечаем событие как обработанное
            await self.inbox_repository.mark_as_processed(idempotency_key)

            # Отправляем уведомление об отправке
            try:
                await self.notifications_client.send_notification(
                    message="SHIPPED",
                    reference_id=order.id,
                    idempotency_key=idempotency_key,
                )
            except Exception as e:
                await logger.awarning(
                    "notification_send_failed_on_order_shipped",
                    order_id=str(event.order_id),
                    error=str(e),
                )

            await logger.ainfo(
                "order_marked_as_shipped",
                order_id=str(event.order_id),
                shipment_id=str(event.shipment_id),
            )
        except ValueError as e:
            await logger.awarning(
                "cannot_mark_order_as_shipped",
                order_id=str(event.order_id),
                current_status=order.status.value,
                error=str(e),
            )

    async def process_order_cancelled(
        self,
        event: OrderCancelledEventDTO,
        idempotency_key: str,
    ) -> None:
        """Обработать событие ORDER.CANCELLED.

        Args:
            event: Данные события
            idempotency_key: Ключ идемпотентности

        Raises:
            OrderNotFoundError: Заказ не найден
        """
        await logger.ainfo(
            "processing_order_cancelled_event",
            order_id=str(event.order_id),
            reason=event.reason,
        )

        # Проверяем, не обработали ли мы уже это событие (Inbox паттерн)
        is_new = await self.inbox_repository.save_event(
            event_id=idempotency_key,
            event_type=event.event_type,
            payload=event.model_dump(mode="json"),
        )

        if not is_new:
            await logger.ainfo(
                "order_cancelled_event_already_processed",
                order_id=str(event.order_id),
                idempotency_key=idempotency_key,
            )
            return

        # Получаем заказ
        order = await self.order_repository.get_by_id(event.order_id)
        if not order:
            await logger.aerror(
                "order_not_found_for_cancellation_event",
                order_id=str(event.order_id),
            )
            raise OrderNotFoundError(str(event.order_id))

        # Обновляем статус заказа
        try:
            order.mark_as_cancelled()
            await self.order_repository.update(order)

            # Отмечаем событие как обработанное
            await self.inbox_repository.mark_as_processed(idempotency_key)

            # Отправляем уведомление об отмене
            try:
                await self.notifications_client.send_notification(
                    message=f"Order cancelled: {event.reason}",
                    reference_id=order.id,
                    idempotency_key=f"order-cancelled-shipping-{order.id}",
                )
            except Exception as e:
                await logger.awarning(
                    "notification_send_failed_on_order_cancelled_from_shipping",
                    order_id=str(event.order_id),
                    error=str(e),
                )

            await logger.ainfo(
                "order_marked_as_cancelled_from_shipping",
                order_id=str(event.order_id),
                reason=event.reason,
            )
        except ValueError as e:
            await logger.awarning(
                "cannot_cancel_order_from_shipping",
                order_id=str(event.order_id),
                current_status=order.status.value,
                error=str(e),
            )
