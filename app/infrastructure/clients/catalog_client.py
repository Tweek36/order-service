"""HTTP клиент для Catalog Service."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import structlog

from app.domain.exceptions import ItemNotFoundError
from app.infrastructure.clients.base_client import BaseHTTPClient
from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


@dataclass
class CatalogItem:
    """Модель товара из каталога."""

    id: UUID
    name: str
    price: Decimal
    available_qty: int


class CatalogClient(BaseHTTPClient):
    """Клиент для взаимодействия с Catalog Service."""

    def __init__(self):
        super().__init__(settings.CAPASHINO_BASE_URL, settings.X_API_KEY)

    async def get_item(self, item_id: UUID) -> CatalogItem:
        """Получить товар по ID.

        Args:
            item_id: ID товара

        Returns:
            Информация о товаре

        Raises:
            ItemNotFoundError: Если товар не найден
        """
        try:
            data = await self._get(f"/api/catalog/items/{item_id}")

            await logger.ainfo(
                "catalog_item_retrieved",
                item_id=str(item_id),
                available_qty=data["available_qty"],
            )

            return CatalogItem(
                id=UUID(data["id"]),
                name=data["name"],
                price=Decimal(data["price"]),
                available_qty=data["available_qty"],
            )
        except Exception as e:
            await logger.aerror(
                "catalog_item_not_found",
                item_id=str(item_id),
                error=str(e),
            )
            raise ItemNotFoundError(str(item_id)) from e
