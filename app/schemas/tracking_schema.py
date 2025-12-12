from datetime import datetime
from pydantic import BaseModel

from app.schemas.order_schema import OrderStatus


class TrackingAddressPublic(BaseModel):
    """Endereço público (sem dados sensíveis)"""
    city: str
    state: str

    class Config:
        from_attributes = True


class TrackingEvent(BaseModel):
    """Evento de tracking para timeline"""
    status: OrderStatus
    status_label: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrackingResponse(BaseModel):
    """Resposta pública de rastreio com timeline"""
    tracking_code: str
    status: OrderStatus
    status_label: str
    origin: TrackingAddressPublic
    destination: TrackingAddressPublic
    events: list[TrackingEvent]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
