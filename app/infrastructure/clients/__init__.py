"""HTTP клиенты для внешних сервисов."""

from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.payments_client import PaymentsClient

__all__ = ["CatalogClient", "PaymentsClient"]
