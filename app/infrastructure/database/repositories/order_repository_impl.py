"""Реализация репозитория заказов."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import OrderStatus
from app.domain.exceptions import DuplicateOrderError
from app.domain.models.order import Order
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.database.models import IdempotencyKeyORM, OrderORM

logger = structlog.get_logger(__name__)


class OrderRepositoryImpl(IOrderRepository):
    """Реализация репозитория заказов с использованием SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order, idempotency_key: str) -> Order:
        """Создать новый заказ.

        Args:
            order: Заказ для создания
            idempotency_key: Ключ идемпотентности

        Returns:
            Созданный заказ

        Raises:
            DuplicateOrderError: Если заказ с таким ключом уже существует
        """
        # Проверяем идемпотентность
        existing_order = await self.get_by_idempotency_key(idempotency_key)
        if existing_order:
            await logger.awarning(
                "duplicate_order_attempt",
                idempotency_key=idempotency_key,
                existing_order_id=str(existing_order.id),
            )
            raise DuplicateOrderError(idempotency_key, str(existing_order.id))

        # Создаем заказ
        order_orm = OrderORM(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status.value,
            payment_id=order.payment_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        self.session.add(order_orm)

        # Сохраняем ключ идемпотентности
        idempotency_orm = IdempotencyKeyORM(
            key=idempotency_key,
            order_id=order.id,
        )
        self.session.add(idempotency_orm)

        await self.session.flush()

        await logger.ainfo(
            "order_created_in_db",
            order_id=str(order.id),
            idempotency_key=idempotency_key,
        )

        return order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID.

        Args:
            order_id: ID заказа

        Returns:
            Заказ или None если не найден
        """
        stmt = select(OrderORM).where(OrderORM.id == order_id)
        result = await self.session.execute(stmt)
        order_orm = result.scalar_one_or_none()

        if not order_orm:
            return None

        return self._to_domain(order_orm)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        """Получить заказ по ключу идемпотентности.

        Args:
            idempotency_key: Ключ идемпотентности

        Returns:
            Заказ или None если не найден
        """
        stmt = select(IdempotencyKeyORM).where(IdempotencyKeyORM.key == idempotency_key)
        result = await self.session.execute(stmt)
        idempotency_orm = result.scalar_one_or_none()

        if not idempotency_orm:
            return None

        return await self.get_by_id(idempotency_orm.order_id)

    async def update(self, order: Order) -> Order:
        """Обновить заказ.

        Args:
            order: Заказ для обновления

        Returns:
            Обновленный заказ
        """
        stmt = select(OrderORM).where(OrderORM.id == order.id)
        result = await self.session.execute(stmt)
        order_orm = result.scalar_one_or_none()

        if order_orm:
            order_orm.status = order.status.value
            order_orm.payment_id = order.payment_id
            order_orm.updated_at = order.updated_at
            await self.session.flush()

            await logger.ainfo(
                "order_updated_in_db",
                order_id=str(order.id),
                new_status=order.status.value,
            )

        return order

    def _to_domain(self, order_orm: OrderORM) -> Order:
        """Преобразовать ORM модель в domain модель.

        Args:
            order_orm: ORM модель заказа

        Returns:
            Domain модель заказа
        """
        return Order(
            id=order_orm.id,
            user_id=order_orm.user_id,
            item_id=order_orm.item_id,
            quantity=order_orm.quantity,
            status=OrderStatus(order_orm.status),
            created_at=order_orm.created_at,
            updated_at=order_orm.updated_at,
            payment_id=order_orm.payment_id,
        )
