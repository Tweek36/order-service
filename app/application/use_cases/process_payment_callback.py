"""Use case для обработки callback от Payments Service."""

from uuid import UUID

import structlog

from app.domain.exceptions import OrderNotFoundError
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.clients.notifications_client import NotificationsClient
from app.infrastructure.database.repositories.outbox_repository import OutboxRepository

logger = structlog.get_logger(__name__)


class ProcessPaymentCallbackUseCase:
    """Use case для обработки результатов платежа."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        outbox_repository: OutboxRepository,
        notifications_client: NotificationsClient,
    ):
        self.order_repository = order_repository
        self.outbox_repository = outbox_repository
        self.notifications_client = notifications_client

    async def execute(
        self,
        payment_id: UUID,
        order_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Обработать результат платежа.

        Args:
            payment_id: ID платежа
            order_id: ID заказа
            status: Статус платежа (succeeded/failed)
            error_message: Сообщение об ошибке (если есть)

        Raises:
            OrderNotFoundError: Заказ не найден
        """
        await logger.ainfo(
            "processing_payment_callback",
            payment_id=str(payment_id),
            order_id=str(order_id),
            status=status,
        )

        # Получаем заказ
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            await logger.aerror(
                "order_not_found_for_payment_callback",
                order_id=str(order_id),
                payment_id=str(payment_id),
            )
            raise OrderNotFoundError(str(order_id))

        # Проверяем, что payment_id совпадает
        if order.payment_id != payment_id:
            await logger.awarning(
                "payment_id_mismatch",
                order_id=str(order_id),
                expected_payment_id=str(order.payment_id),
                received_payment_id=str(payment_id),
            )
            # Игнорируем callback с неправильным payment_id (идемпотентность)
            return

        # Обрабатываем статус платежа
        if status == "succeeded":
            try:
                order.mark_as_paid()
                await self.order_repository.update(order)

                # Сохраняем событие ORDER.PAID в outbox для отправки в Shipping Service
                await self.outbox_repository.save_event(
                    aggregate_id=order.id,
                    event_type="order.paid",
                    payload={
                        "order_id": str(order.id),
                        "item_id": str(order.item_id),
                        "quantity": order.quantity,
                        "idempotency_key": f"order-paid-{order.id}",
                    },
                )

                # Отправляем уведомление об успешной оплате
                try:
                    await self.notifications_client.send_notification(
                        message=(
                            "Order PAID: Your order has been successfully "
                            "paid and is ready for shipment"
                        ),
                        reference_id=order.id,
                        idempotency_key=f"order-paid-{order.id}",
                    )
                except Exception as e:
                    await logger.awarning(
                        "notification_send_failed_on_order_paid",
                        order_id=str(order_id),
                        error=str(e),
                    )

                await logger.ainfo(
                    "order_marked_as_paid",
                    order_id=str(order_id),
                    payment_id=str(payment_id),
                )
            except ValueError as e:
                # Заказ уже в другом статусе (идемпотентность)
                await logger.awarning(
                    "cannot_mark_order_as_paid",
                    order_id=str(order_id),
                    current_status=order.status.value,
                    error=str(e),
                )
        elif status == "failed":
            try:
                order.mark_as_cancelled()
                await self.order_repository.update(order)
                # Отправляем уведомление об отмене
                try:
                    cancel_reason = error_message or "Платеж не прошел"
                    await self.notifications_client.send_notification(
                        message=f"Order cancelled. Reason: {cancel_reason}",
                        reference_id=order.id,
                        idempotency_key=f"order-cancelled-payment-{order.id}",
                    )
                except Exception as e:
                    await logger.awarning(
                        "notification_send_failed_on_order_cancelled",
                        order_id=str(order_id),
                        error=str(e),
                    )

                await logger.ainfo(
                    "order_cancelled_due_to_failed_payment",
                    order_id=str(order_id),
                    payment_id=str(payment_id),
                    error_message=error_message,
                )
            except ValueError as e:
                # Заказ уже в другом статусе (идемпотентность)
                await logger.awarning(
                    "cannot_cancel_order",
                    order_id=str(order_id),
                    current_status=order.status.value,
                    error=str(e),
                )
        else:
            await logger.awarning(
                "unknown_payment_status",
                order_id=str(order_id),
                payment_id=str(payment_id),
                status=status,
            )
