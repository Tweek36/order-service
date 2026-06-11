"""DTO для Catalog Service."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CatalogItem:
    """Модель товара из каталога."""

    id: UUID
    name: str
    price: Decimal
    available_qty: int
