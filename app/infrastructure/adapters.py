"""Адаптеры для реализации интерфейсов из слоя Application."""

from app.application.ports import (
    ICatalogClient,
    IInboxRepository,
    INotificationsClient,
    IOutboxRepository,
    IPaymentsClient,
)
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.notifications_client import NotificationsClient
from app.infrastructure.clients.payments_client import PaymentsClient
from app.infrastructure.database.repositories.inbox_repository import InboxRepository
from app.infrastructure.database.repositories.outbox_repository import OutboxRepository


class CatalogClientAdapter(CatalogClient, ICatalogClient):
    """Адаптер для CatalogClient, реализующий ICatalogClient."""

    pass


class NotificationsClientAdapter(NotificationsClient, INotificationsClient):
    """Адаптер для NotificationsClient, реализующий INotificationsClient."""

    pass


class PaymentsClientAdapter(PaymentsClient, IPaymentsClient):
    """Адаптер для PaymentsClient, реализующий IPaymentsClient."""

    pass


class OutboxRepositoryAdapter(OutboxRepository, IOutboxRepository):
    """Адаптер для OutboxRepository, реализующий IOutboxRepository."""

    pass


class InboxRepositoryAdapter(InboxRepository, IInboxRepository):
    """Адаптер для InboxRepository, реализующий IInboxRepository."""

    pass
