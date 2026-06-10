"""Endpoints для заказов."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.order_dto import CreateOrderDTO
from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.exceptions import (
    DuplicateOrderError,
    InsufficientStockError,
    ItemNotFoundError,
    OrderNotFoundError,
)
from app.domain.repositories.order_repository import IOrderRepository
from app.infrastructure.database.session import get_async_session
from app.presentation.api.dependencies import (
    get_create_order_use_case,
    get_order_repository,
)
from app.presentation.schemas.order_schema import CreateOrderRequest, OrderResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])
logger = structlog.get_logger(__name__)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    use_case: Annotated[CreateOrderUseCase, Depends(get_create_order_use_case)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> OrderResponse:
    """Создать новый заказ."""
    try:
        dto = CreateOrderDTO(
            user_id=request.user_id,
            item_id=request.item_id,
            quantity=request.quantity,
            idempotency_key=request.idempotency_key,
        )

        order_dto = await use_case.execute(dto)
        await session.commit()

        return OrderResponse(
            id=order_dto.id,
            user_id=order_dto.user_id,
            item_id=order_dto.item_id,
            quantity=order_dto.quantity,
            status=order_dto.status,
            created_at=order_dto.created_at,
            updated_at=order_dto.updated_at,
        )
    except ItemNotFoundError as e:
        await logger.aerror("item_not_found", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item {e.item_id} not found in catalog",
        )
    except InsufficientStockError as e:
        await logger.awarning("insufficient_stock", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient stock: requested {e.requested}, "
                f"available {e.available}"
            ),
        )
    except DuplicateOrderError as e:
        await logger.awarning("duplicate_order", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Order with idempotency key {e.idempotency_key} " f"already exists"
            ),
        )
    except Exception as e:
        await session.rollback()
        await logger.aerror("create_order_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    order_repo: Annotated[IOrderRepository, Depends(get_order_repository)],
) -> OrderResponse:
    """Получить заказ по ID."""
    try:
        order = await order_repo.get_by_id(order_id)

        if not order:
            raise OrderNotFoundError(str(order_id))

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    except OrderNotFoundError:
        await logger.awarning("order_not_found", order_id=str(order_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )
    except Exception as e:
        await logger.aerror("get_order_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order",
        )
