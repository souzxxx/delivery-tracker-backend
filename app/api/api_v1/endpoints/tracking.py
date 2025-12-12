from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_event import STATUS_LABELS
from app.schemas.tracking_schema import TrackingResponse, TrackingAddressPublic, TrackingEvent
from app.services.db_service import get_db

router = APIRouter()


@router.get("/{tracking_code}", response_model=TrackingResponse)
def track_order(
    tracking_code: str,
    db: Session = Depends(get_db),
):
    """
    🔓 Rota PÚBLICA - Não requer autenticação
    
    Consulta o status de um pedido pelo código de rastreio.
    Retorna timeline completa de eventos + informações públicas.
    """
    order = (
        db.query(Order)
        .filter(Order.tracking_code == tracking_code.upper())
        .first()
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de rastreio não encontrado.",
        )
    
    # Monta lista de eventos
    events = [
        TrackingEvent(
            status=event.status,
            status_label=event.status_label,
            description=event.description,
            created_at=event.created_at,
        )
        for event in order.events
    ]
    
    return TrackingResponse(
        tracking_code=order.tracking_code,
        status=order.status,
        status_label=STATUS_LABELS.get(order.status, order.status),
        origin=TrackingAddressPublic(
            city=order.origin_address.city,
            state=order.origin_address.state,
        ),
        destination=TrackingAddressPublic(
            city=order.destination_address.city,
            state=order.destination_address.state,
        ),
        events=events,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
