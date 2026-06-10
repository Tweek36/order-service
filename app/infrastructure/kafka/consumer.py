"""Kafka consumer для обработки событий от Shipping Service."""

import asyncio
import json

import structlog
from aiokafka import AIOKafkaConsumer

from app.application.dto.shipping_event_dto import (
    OrderCancelledEventDTO,
    OrderShippedEventDTO,
)
from app.application.use_cases.process_shipping_event import (
    ProcessShippingEventUseCase,
)
from app.infrastructure.clients.notifications_client import NotificationsClient
from app.infrastructure.database.repositories.inbox_repository import InboxRepository
from app.infrastructure.database.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.infrastructure.database.session import async_session_maker
from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class KafkaConsumer:
    """Kafka consumer для обработки событий от Shipping Service."""

    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.topic = settings.KAFKA_SHIPMENT_EVENTS_TOPIC
        self.group_id = settings.KAFKA_CONSUMER_GROUP
        self.running = False

    async def start(self) -> None:
        """Запустить consumer."""
        try:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            await self.consumer.start()
            await logger.ainfo(
                "kafka_consumer_started",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                topic=self.topic,
                group_id=self.group_id,
            )

            self.running = True
            await self._consume_events()
        except Exception as e:
            await logger.aerror(
                "kafka_consumer_start_failed",
                error=str(e),
            )
            raise

    async def stop(self) -> None:
        """Остановить consumer."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            await logger.ainfo("kafka_consumer_stopped")

    async def _consume_events(self) -> None:
        """Потреблять события из Kafka."""
        if not self.consumer:
            return

        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    event_data = message.value
                    await self._process_event(event_data)
                except Exception as e:
                    await logger.aerror(
                        "kafka_event_processing_failed",
                        error=str(e),
                        event_data=message.value,
                    )
        except Exception as e:
            await logger.aerror(
                "kafka_consumer_error",
                error=str(e),
            )

    async def _process_event(self, event_data: dict) -> None:
        """Обработать событие.

        Args:
            event_data: Данные события
        """
        event_type = event_data.get("event_type")

        await logger.ainfo(
            "kafka_event_received",
            event_type=event_type,
            order_id=event_data.get("order_id"),
        )

        async with async_session_maker() as session:
            order_repo = OrderRepositoryImpl(session)
            inbox_repo = InboxRepository(session)
            notifications_client = NotificationsClient()
            use_case = ProcessShippingEventUseCase(
                order_repo, inbox_repo, notifications_client
            )

            try:
                if event_type == "order.shipped":
                    event = OrderShippedEventDTO(**event_data)
                    # Используем order_id и shipment_id для идемпотентности
                    idempotency_key = (
                        f"shipped-{str(event.order_id)}-{str(event.shipment_id)}"
                    )
                    await use_case.process_order_shipped(event, idempotency_key)
                elif event_type == "order.cancelled":
                    event = OrderCancelledEventDTO(**event_data)
                    # Используем order_id для идемпотентности
                    idempotency_key = f"cancelled-{str(event.order_id)}"
                    await use_case.process_order_cancelled(event, idempotency_key)
                else:
                    await logger.awarning(
                        "unknown_event_type",
                        event_type=event_type,
                    )
                    return

                await session.commit()

                await logger.ainfo(
                    "kafka_event_processed",
                    event_type=event_type,
                    order_id=event_data.get("order_id"),
                )
            except Exception as e:
                await session.rollback()
                await logger.aerror(
                    "event_processing_failed",
                    event_type=event_type,
                    error=str(e),
                )
                raise


# Глобальный экземпляр consumer
_consumer: KafkaConsumer | None = None


async def start_kafka_consumer() -> None:
    """Запустить Kafka consumer в фоновой задаче."""
    global _consumer
    if _consumer is None:
        _consumer = KafkaConsumer()
        asyncio.create_task(_consumer.start())


async def stop_kafka_consumer() -> None:
    """Остановить Kafka consumer."""
    global _consumer
    if _consumer:
        await _consumer.stop()
        _consumer = None
