"""DTO для событий от Shipping Service."""

from uuid import UUID

from pydantic import BaseModel


class OrderShippedEventDTO(BaseModel):
    """DTO для события ORDER.SHIPPED."""

    event_type: str
    order_id: UUID
    item_id: UUID
    quantity: int
    shipment_id: UUID


class OrderCancelledEventDTO(BaseModel):
    """DTO для события ORDER.CANCELLED."""

    event_type: str
    order_id: UUID
    item_id: UUID
    quantity: int
    reason: str
