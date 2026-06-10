"""FastAPI зависимости."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.process_payment_callback import (
    ProcessPaymentCallbackUseCase,
)
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.notifications_client import NotificationsClient
from app.infrastructure.clients.payments_client import PaymentsClient
from app.infrastructure.database.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.infrastructure.database.repositories.outbox_repository import (
    OutboxRepository,
)
from app.infrastructure.database.session import get_async_session


async def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IOrderRepository:
    """Получить репозиторий заказов."""
    return OrderRepositoryImpl(session)


async def get_catalog_client() -> CatalogClient:
    """Получить клиент Catalog Service."""
    return CatalogClient()


async def get_payments_client() -> PaymentsClient:
    """Получить клиент Payments Service."""
    return PaymentsClient()


async def get_notifications_client() -> NotificationsClient:
    """Получить клиент Notifications Service."""
    return NotificationsClient()


async def get_outbox_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> OutboxRepository:
    """Получить репозиторий outbox."""
    return OutboxRepository(session)


async def get_create_order_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    catalog_client: Annotated[CatalogClient, Depends(get_catalog_client)],
    payments_client: Annotated[PaymentsClient, Depends(get_payments_client)],
    notifications_client: Annotated[
        NotificationsClient, Depends(get_notifications_client)
    ],
) -> CreateOrderUseCase:
    """Получить use case создания заказа."""
    return CreateOrderUseCase(
        order_repo, catalog_client, payments_client, notifications_client
    )


async def get_process_payment_callback_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    outbox_repo: Annotated[OutboxRepository, Depends(get_outbox_repository)],
    notifications_client: Annotated[
        NotificationsClient, Depends(get_notifications_client)
    ],
) -> ProcessPaymentCallbackUseCase:
    """Получить use case обработки payment callback."""
    return ProcessPaymentCallbackUseCase(order_repo, outbox_repo, notifications_client)
