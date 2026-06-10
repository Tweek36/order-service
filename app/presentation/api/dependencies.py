"""FastAPI зависимости."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.clients.catalog_client import CatalogClient
from app.infrastructure.clients.payments_client import PaymentsClient
from app.infrastructure.database.repositories.order_repository_impl import (
    OrderRepositoryImpl,
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


async def get_create_order_use_case(
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
    catalog_client: Annotated[CatalogClient, Depends(get_catalog_client)],
    payments_client: Annotated[PaymentsClient, Depends(get_payments_client)],
) -> CreateOrderUseCase:
    """Получить use case создания заказа."""
    return CreateOrderUseCase(order_repo, catalog_client, payments_client)
