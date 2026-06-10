"""Репозиторий для работы с outbox событиями."""

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import OutboxEventORM


class OutboxRepository:
    """Репозиторий для управления outbox событиями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_event(
        self,
        aggregate_id: UUID,
        event_type: str,
        payload: dict,
    ) -> None:
        """Сохранить событие в outbox.

        Args:
            aggregate_id: ID агрегата (заказа)
            event_type: Тип события
            payload: Данные события
        """
        event = OutboxEventORM(
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=json.dumps(payload),
            published=False,
            created_at=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.flush()

    async def get_unpublished_events(self, limit: int = 100) -> list[OutboxEventORM]:
        """Получить неопубликованные события.

        Args:
            limit: Максимальное количество событий

        Returns:
            Список неопубликованных событий
        """
        stmt = (
            select(OutboxEventORM)
            .where(OutboxEventORM.published == False)  # noqa: E712
            .order_by(OutboxEventORM.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_published(self, event_id: UUID) -> None:
        """Отметить событие как опубликованное.

        Args:
            event_id: ID события
        """
        stmt = select(OutboxEventORM).where(OutboxEventORM.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()

        if event:
            event.published = True
            event.published_at = datetime.utcnow()
            await self.session.flush()
