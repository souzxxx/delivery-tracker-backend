from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.address_schema import AddressCreate, AddressResponse


class OrderStatus(str, Enum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class OrderCreate(BaseModel):
    origin_address: AddressCreate
    destination_address: AddressCreate


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    tracking_code: str
    status: OrderStatus
    owner_id: int
    origin_address: AddressResponse
    destination_address: AddressResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Resposta simplificada para listagem"""
    id: int
    tracking_code: str
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True

