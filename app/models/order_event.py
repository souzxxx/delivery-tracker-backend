from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


# Labels amigáveis para cada status
STATUS_LABELS = {
    "created": "Pedido criado",
    "in_transit": "Saiu para entrega",
    "delivered": "Entregue",
    "canceled": "Cancelado",
}


class OrderEvent(Base):
    """Evento de tracking - cada mudança de status gera um evento"""
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com Order
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="events")
    
    # Dados do evento
    status = Column(String(20), nullable=False)
    status_label = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamp do evento
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

