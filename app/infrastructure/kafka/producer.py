"""Kafka producer для публикации событий."""

import json

import structlog
from aiokafka import AIOKafkaProducer

from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class KafkaProducer:
    """Kafka producer для публикации событий в топик."""

    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        self.topic = settings.KAFKA_ORDER_EVENTS_TOPIC

    async def start(self) -> None:
        """Запустить producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self.producer.start()
            await logger.ainfo(
                "kafka_producer_started",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                topic=self.topic,
            )
        except Exception as e:
            await logger.aerror(
                "kafka_producer_start_failed",
                error=str(e),
            )
            raise

    async def stop(self) -> None:
        """Остановить producer."""
        if self.producer:
            await self.producer.stop()
            await logger.ainfo("kafka_producer_stopped")

    async def send_event(self, event_data: dict) -> None:
        """Отправить событие в Kafka.

        Args:
            event_data: Данные события
        """
        if not self.producer:
            raise RuntimeError("Producer not started")

        try:
            await self.producer.send_and_wait(self.topic, event_data)
            await logger.ainfo(
                "kafka_event_sent",
                event_type=event_data.get("event_type"),
                order_id=event_data.get("order_id"),
            )
        except Exception as e:
            await logger.aerror(
                "kafka_event_send_failed",
                event_type=event_data.get("event_type"),
                error=str(e),
            )
            raise


# Глобальный экземпляр producer
_producer: KafkaProducer | None = None


async def get_kafka_producer() -> KafkaProducer:
    """Получить глобальный экземпляр Kafka producer."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer()
        await _producer.start()
    return _producer


async def shutdown_kafka_producer() -> None:
    """Остановить глобальный Kafka producer."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
