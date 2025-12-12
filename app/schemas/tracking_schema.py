from datetime import datetime
from pydantic import BaseModel

from app.schemas.order_schema import OrderStatus


class TrackingAddressPublic(BaseModel):
    """Endereço público (sem dados sensíveis)"""
    city: str
    state: str

    class Config:
        from_attributes = True


class TrackingResponse(BaseModel):
    """Resposta pública de rastreio"""
    tracking_code: str
    status: OrderStatus
    origin: TrackingAddressPublic
    destination: TrackingAddressPublic
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

