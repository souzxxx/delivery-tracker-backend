from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class OrderStatus(str, Enum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(String(20), default=OrderStatus.CREATED.value, nullable=False)
    
    # Relacionamento com User (dono do pedido)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="orders")
    
    # Relacionamento com Address (origem e destino)
    origin_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    destination_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    
    origin_address = relationship("Address", foreign_keys=[origin_address_id])
    destination_address = relationship("Address", foreign_keys=[destination_address_id])
    
    # Relacionamento com eventos de tracking (timeline)
    events = relationship("OrderEvent", back_populates="order", order_by="OrderEvent.created_at.desc()")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

