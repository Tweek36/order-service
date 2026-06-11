"""Порты (интерфейсы) для Application layer."""

from app.application.ports.catalog_service import ICatalogService
from app.application.ports.clients import (
    ICatalogClient,
    IInboxRepository,
    INotificationsClient,
    IOutboxRepository,
    IPaymentsClient,
)

__all__ = [
    "ICatalogService",
    "ICatalogClient",
    "INotificationsClient",
    "IPaymentsClient",
    "IOutboxRepository",
    "IInboxRepository",
]
