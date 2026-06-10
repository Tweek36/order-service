"""Фоновая задача для публикации событий из Outbox в Kafka."""

import asyncio
import json

import structlog

from app.infrastructure.database.repositories.outbox_repository import OutboxRepository
from app.infrastructure.database.session import async_session_maker
from app.infrastructure.kafka.producer import get_kafka_producer

logger = structlog.get_logger(__name__)


class OutboxPublisher:
    """Публикатор событий из Outbox в Kafka."""

    def __init__(self, poll_interval: int = 5):
        """Инициализация публикатора.

        Args:
            poll_interval: Интервал опроса outbox в секундах
        """
        self.poll_interval = poll_interval
        self.running = False

    async def start(self) -> None:
        """Запустить публикатор."""
        self.running = True
        await logger.ainfo("outbox_publisher_started", poll_interval=self.poll_interval)

        while self.running:
            try:
                await self._publish_events()
            except Exception as e:
                await logger.aerror(
                    "outbox_publisher_error",
                    error=str(e),
                )
            await asyncio.sleep(self.poll_interval)

    async def stop(self) -> None:
        """Остановить публикатор."""
        self.running = False
        await logger.ainfo("outbox_publisher_stopped")

    async def _publish_events(self) -> None:
        """Опубликовать неопубликованные события."""
        async with async_session_maker() as session:
            outbox_repo = OutboxRepository(session)
            producer = await get_kafka_producer()

            # Получаем неопубликованные события
            events = await outbox_repo.get_unpublished_events(limit=100)

            if not events:
                return

            await logger.ainfo("publishing_outbox_events", count=len(events))

            for event in events:
                try:
                    # Парсим payload
                    payload = json.loads(event.payload)

                    # Отправляем в Kafka
                    await producer.send_event(payload)

                    # Отмечаем как опубликованное
                    await outbox_repo.mark_as_published(event.id)
                    await session.commit()

                    await logger.ainfo(
                        "outbox_event_published",
                        event_id=str(event.id),
                        event_type=event.event_type,
                        aggregate_id=str(event.aggregate_id),
                    )
                except Exception as e:
                    await logger.aerror(
                        "outbox_event_publish_failed",
                        event_id=str(event.id),
                        error=str(e),
                    )
                    await session.rollback()


# Глобальный экземпляр publisher
_publisher: OutboxPublisher | None = None


async def start_outbox_publisher() -> None:
    """Запустить фоновую задачу публикатора."""
    global _publisher
    if _publisher is None:
        _publisher = OutboxPublisher()
        asyncio.create_task(_publisher.start())


async def stop_outbox_publisher() -> None:
    """Остановить фоновую задачу публикатора."""
    global _publisher
    if _publisher:
        await _publisher.stop()
        _publisher = None
