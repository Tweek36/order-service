"""Интерфейс для Catalog Service."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.infrastructure.clients.catalog_client import CatalogItem


class ICatalogService(ABC):
    """Интерфейс сервиса каталога."""

    @abstractmethod
    async def get_item(self, item_id: UUID) -> CatalogItem:
        """Получить товар по ID."""
        pass
