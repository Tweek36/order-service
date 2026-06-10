"""Интерфейс репозитория заказов."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.order import Order


class IOrderRepository(ABC):
    """Интерфейс репозитория для работы с заказами."""

    @abstractmethod
    async def create(self, order: Order, idempotency_key: str) -> Order:
        """Создать новый заказ.

        Args:
            order: Заказ для создания
            idempotency_key: Ключ идемпотентности

        Returns:
            Созданный заказ
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID.

        Args:
            order_id: ID заказа

        Returns:
            Заказ или None если не найден
        """
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        """Получить заказ по ключу идемпотентности.

        Args:
            idempotency_key: Ключ идемпотентности

        Returns:
            Заказ или None если не найден
        """
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Обновить заказ.

        Args:
            order: Заказ для обновления

        Returns:
            Обновленный заказ
        """
        pass
