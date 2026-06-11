"""FastAPI зависимости."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports import (
    ICatalogClient,
    IInboxRepository,
    INotificationsClient,
    IOutboxRepository,
    IPaymentsClient,
)
from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.process_payment_callback import (
    ProcessPaymentCallbackUseCase,
)
from app.application.use_cases.process_shipping_event import ProcessShippingEventUseCase
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.adapters import (
    CatalogClientAdapter,
    InboxRepositoryAdapter,
    NotificationsClientAdapter,
    OutboxRepositoryAdapter,
    PaymentsClientAdapter,
)
from app.infrastructure.database.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from app.infrastructure.database.session import get_async_session
from app.settings import get_settings


async def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IOrderRepository:
    """Получить репозиторий заказов."""
    return OrderRepositoryImpl(session)


async def get_catalog_client() -> ICatalogClient:
    """Получить клиент Catalog Service."""
    return CatalogClientAdapter()


async def get_payments_client() -> IPaymentsClient:
    """Получить клиент Payments Service."""
    return PaymentsClientAdapter()


async def get_notifications_client() -> INotificationsClient:
    """Получить клиент Notifications Service."""
    return NotificationsClientAdapter()


async def get_outbox_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IOutboxRepository:
    """Получить репозиторий outbox."""
    return OutboxRepositoryAdapter(session)


async def get_inbox_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IInboxRepository:
    """Получить репозиторий inbox."""
    return InboxRepositoryAdapter(session)


async def get_create_order_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    catalog_client: Annotated[ICatalogClient, Depends(get_catalog_client)],
    payments_client: Annotated[IPaymentsClient, Depends(get_payments_client)],
    notifications_client: Annotated[
        INotificationsClient, Depends(get_notifications_client)
    ],
) -> CreateOrderUseCase:
    """Получить use case создания заказа."""
    settings = get_settings()
    return CreateOrderUseCase(
        order_repo,
        catalog_client,
        payments_client,
        notifications_client,
        settings.callback_url,
    )


async def get_process_payment_callback_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    outbox_repo: Annotated[IOutboxRepository, Depends(get_outbox_repository)],
    notifications_client: Annotated[
        INotificationsClient, Depends(get_notifications_client)
    ],
) -> ProcessPaymentCallbackUseCase:
    """Получить use case обработки payment callback."""
    return ProcessPaymentCallbackUseCase(order_repo, outbox_repo, notifications_client)


async def get_process_shipping_event_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    inbox_repo: Annotated[IInboxRepository, Depends(get_inbox_repository)],
    notifications_client: Annotated[
        INotificationsClient, Depends(get_notifications_client)
    ],
) -> ProcessShippingEventUseCase:
    """Получить use case обработки событий от Shipping Service."""
    return ProcessShippingEventUseCase(order_repo, inbox_repo, notifications_client)
