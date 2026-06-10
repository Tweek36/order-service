"""Репозиторий для работы с inbox событиями."""

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import InboxEventORM


class InboxRepository:
    """Репозиторий для управления inbox событиями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def event_exists(self, event_id: str) -> bool:
        """Проверить, существует ли событие.

        Args:
            event_id: ID события

        Returns:
            True если событие существует
        """
        stmt = select(InboxEventORM).where(InboxEventORM.id == event_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def save_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict,
    ) -> bool:
        """Сохранить событие в inbox.

        Args:
            event_id: ID события (для идемпотентности)
            event_type: Тип события
            payload: Данные события

        Returns:
            True если событие было сохранено, False если уже существует
        """
        if await self.event_exists(event_id):
            return False

        event = InboxEventORM(
            id=event_id,
            event_type=event_type,
            payload=json.dumps(payload),
            processed=False,
            created_at=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.flush()
        return True

    async def mark_as_processed(self, event_id: str) -> None:
        """Отметить событие как обработанное.

        Args:
            event_id: ID события
        """
        stmt = select(InboxEventORM).where(InboxEventORM.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()

        if event:
            event.processed = True
            event.processed_at = datetime.utcnow()
            await self.session.flush()
