"""Интерфейсы для клиентов внешних сервисов."""

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.infrastructure.clients.catalog_client import CatalogItem
from app.infrastructure.clients.payments_client import PaymentResponse


class ICatalogClient(ABC):
    """Интерфейс клиента Catalog Service."""

    @abstractmethod
    async def get_item(self, item_id: UUID) -> CatalogItem:
        """Получить товар по ID."""
        pass

    @abstractmethod
    async def get_item_by_name(self, item_name: str) -> CatalogItem:
        """Получить товар по имени."""
        pass


class INotificationsClient(ABC):
    """Интерфейс клиента Notifications Service."""

    @abstractmethod
    async def send_notification(
        self,
        message: str,
        reference_id: UUID,
        idempotency_key: str,
    ) -> dict | None:
        """Отправить уведомление.

        Returns:
            Данные созданного уведомления или None в случае ошибки
        """
        pass


class IPaymentsClient(ABC):
    """Интерфейс клиента Payments Service."""

    @abstractmethod
    async def create_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        callback_url: str,
        idempotency_key: str,
    ) -> PaymentResponse:
        """Создать платеж."""
        pass


class IOutboxRepository(ABC):
    """Интерфейс репозитория для Outbox."""

    @abstractmethod
    async def save_event(
        self,
        aggregate_id: UUID,
        event_type: str,
        payload: dict,
    ) -> None:
        """Сохранить событие в outbox."""
        pass


class IInboxRepository(ABC):
    """Интерфейс репозитория для Inbox."""

    @abstractmethod
    async def save_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict,
    ) -> bool:
        """Сохранить событие в inbox.

        Returns:
            True, если событие новое, False если уже было обработано.
        """
        pass

    @abstractmethod
    async def mark_as_processed(self, event_id: str) -> None:
        """Отметить событие как обработанное."""
        pass
