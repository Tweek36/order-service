"""Use case для создания заказа."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import structlog

from app.application.dto.catalog_dto import CatalogItem
from app.application.dto.order_dto import CreateOrderDTO, OrderDTO
from app.application.ports import ICatalogClient, INotificationsClient, IPaymentsClient
from app.domain.enums import OrderStatus
from app.domain.exceptions import InsufficientStockError
from app.domain.models.order import Order
from app.domain.repositories.order_repository import IOrderRepository

logger = structlog.get_logger(__name__)


class CreateOrderUseCase:
    """Use case для создания нового заказа."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        catalog_client: ICatalogClient,
        payments_client: IPaymentsClient,
        notifications_client: INotificationsClient,
        callback_url: str,
    ):
        self.order_repository = order_repository
        self.catalog_client = catalog_client
        self.payments_client = payments_client
        self.notifications_client = notifications_client
        self.callback_url = callback_url

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

        # Отправляем уведомление о создании заказа
        try:
            await self.notifications_client.send_notification(
                message="NEW",
                reference_id=order.id,
                idempotency_key=f"order-created-{order.id}",
            )
        except Exception as e:
            # Не блокируем процесс, только логируем
            await logger.awarning(
                "notification_send_failed_on_order_created",
                order_id=str(order.id),
                error=str(e),
            )

        # Создаем платеж через Payments Service
        try:
            # Рассчитываем сумму платежа
            amount = Decimal(catalog_item.price) * dto.quantity

            payment = await self.payments_client.create_payment(
                order_id=order.id,
                amount=amount,
                callback_url=self.callback_url,
                idempotency_key=dto.idempotency_key,
            )

            # Сохраняем payment_id в заказе
            order.payment_id = payment.id
            order = await self.order_repository.update(order)

            await logger.ainfo(
                "payment_created",
                order_id=str(order.id),
                payment_id=str(payment.id),
                amount=amount,
            )
        except Exception as e:
            # Если не удалось создать платеж, отменяем заказ
            await logger.aerror(
                "payment_creation_failed",
                order_id=str(order.id),
                error=str(e),
            )
            order.mark_as_cancelled()
            await self.order_repository.update(order)
            raise

        return OrderDTO(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    async def get_item_by_name(self, item_name: str) -> CatalogItem:
        """Получить товар по имени."""
        return await self.catalog_client.get_item_by_name(item_name)
