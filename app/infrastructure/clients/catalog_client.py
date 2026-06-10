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
        super().__init__(settings.CATALOG_SERVICE_URL, settings.API_TOKEN)

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

    async def get_item_by_name(self, item_name: str) -> CatalogItem:
        """Получить товар по названию.

        Args:
            item_name: Название товара

        Returns:
            Информация о товаре

        Raises:
            ItemNotFoundError: Если товар не найден
        """
        try:
            # Получаем список всех товаров и ищем по имени
            data = await self._get("/api/catalog/items")
            items = data.get("items", [])

            for item_data in items:
                if item_data["name"] == item_name:
                    await logger.ainfo(
                        "catalog_item_retrieved_by_name",
                        item_name=item_name,
                        item_id=item_data["id"],
                        available_qty=item_data["available_qty"],
                    )

                    return CatalogItem(
                        id=UUID(item_data["id"]),
                        name=item_data["name"],
                        price=Decimal(item_data["price"]),
                        available_qty=item_data["available_qty"],
                    )

            # Товар не найден
            await logger.aerror(
                "catalog_item_not_found_by_name",
                item_name=item_name,
            )
            raise ItemNotFoundError(item_name)
        except ItemNotFoundError:
            raise
        except Exception as e:
            await logger.aerror(
                "catalog_item_search_failed",
                item_name=item_name,
                error=str(e),
            )
            raise ItemNotFoundError(item_name) from e
