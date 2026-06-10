"""Use case для создания заказа."""

from datetime import datetime
from uuid import uuid4

import structlog

from app.application.dto.order_dto import CreateOrderDTO, OrderDTO
from app.domain.enums import OrderStatus
from app.domain.exceptions import InsufficientStockError
from app.domain.models.order import Order
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.clients.catalog_client import CatalogClient

logger = structlog.get_logger(__name__)


class CreateOrderUseCase:
    """Use case для создания нового заказа."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        catalog_client: CatalogClient,
    ):
        self.order_repository = order_repository
        self.catalog_client = catalog_client

    async def execute(self, dto: CreateOrderDTO) -> OrderDTO:
        """Создать новый заказ.

        Args:
            dto: Данные для создания заказа

        Returns:
            Созданный заказ

        Raises:
            InsufficientStockError: Недостаточно товара на складе
            ItemNotFoundError: Товар не найден
            DuplicateOrderError: Попытка создать дубликат заказа
        """
        await logger.ainfo(
            "create_order_use_case_started",
            user_id=dto.user_id,
            item_id=str(dto.item_id),
            quantity=dto.quantity,
            idempotency_key=dto.idempotency_key,
        )

        # Проверяем наличие товара через Catalog Service
        catalog_item = await self.catalog_client.get_item(dto.item_id)

        # Проверяем доступное количество
        if catalog_item.available_qty < dto.quantity:
            await logger.awarning(
                "insufficient_stock",
                item_id=str(dto.item_id),
                requested=dto.quantity,
                available=catalog_item.available_qty,
            )
            raise InsufficientStockError(
                str(dto.item_id), dto.quantity, catalog_item.available_qty
            )

        # Создаем заказ
        now = datetime.utcnow()
        order = Order(
            id=uuid4(),
            user_id=dto.user_id,
            item_id=dto.item_id,
            quantity=dto.quantity,
            status=OrderStatus.NEW,
            created_at=now,
            updated_at=now,
        )

        # Сохраняем заказ
        order = await self.order_repository.create(order, dto.idempotency_key)

        await logger.ainfo(
            "order_created",
            order_id=str(order.id),
            status=order.status.value,
        )

        return OrderDTO(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
