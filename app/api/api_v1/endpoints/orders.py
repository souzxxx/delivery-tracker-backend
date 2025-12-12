import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.address import Address
from app.models.order import Order, OrderStatus
from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate,
)
from app.services.db_service import get_db
from app.services.auth_service import get_current_user

router = APIRouter()


def generate_tracking_code() -> str:
    """Gera um código de rastreio único"""
    return f"DT-{uuid.uuid4().hex[:8].upper()}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo pedido com endereços de origem e destino"""
    
    # Cria endereço de origem
    origin = Address(
        cep=order_data.origin_address.cep,
        street=order_data.origin_address.street,
        number=order_data.origin_address.number,
        complement=order_data.origin_address.complement,
        city=order_data.origin_address.city,
        state=order_data.origin_address.state,
    )
    db.add(origin)
    
    # Cria endereço de destino
    destination = Address(
        cep=order_data.destination_address.cep,
        street=order_data.destination_address.street,
        number=order_data.destination_address.number,
        complement=order_data.destination_address.complement,
        city=order_data.destination_address.city,
        state=order_data.destination_address.state,
    )
    db.add(destination)
    
    # Flush para obter os IDs dos endereços
    db.flush()
    
    # Cria o pedido
    order = Order(
        tracking_code=generate_tracking_code(),
        status=OrderStatus.CREATED.value,
        owner_id=current_user.id,
        origin_address_id=origin.id,
        destination_address_id=destination.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/", response_model=list[OrderListResponse])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os pedidos do usuário logado"""
    orders = (
        db.query(Order)
        .filter(Order.owner_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna detalhes de um pedido específico"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )
    
    # Verifica se o pedido pertence ao usuário
    if order.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este pedido.",
        )
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza o status de um pedido"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )
    
    # Verifica se o pedido pertence ao usuário
    if order.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para modificar este pedido.",
        )
    
    # Validação de transição de status
    current_status = order.status
    new_status = status_update.status.value
    
    # Não permite alterar pedido já entregue ou cancelado
    if current_status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível alterar um pedido com status '{current_status}'.",
        )
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return order

