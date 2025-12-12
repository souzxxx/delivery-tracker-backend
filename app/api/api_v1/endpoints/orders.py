import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.address import Address
from app.models.order import Order, OrderStatus
from app.models.order_event import OrderEvent, STATUS_LABELS
from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate,
)
from app.schemas.address_schema import AddressCreateByCEP
from app.services.db_service import get_db
from app.services.auth_service import get_current_user, get_current_admin
from app.models.user import UserRole
from app.services.viacep_service import fetch_address_by_cep, AddressFromCEP
from app.services.geocoding_service import geocode_address, geocode_by_cep, Coordinates

router = APIRouter()


def generate_tracking_code() -> str:
    """Gera um código de rastreio único"""
    return f"DT-{uuid.uuid4().hex[:8].upper()}"


def create_order_event(
    db: Session,
    order_id: int,
    new_status: str,
    description: str | None = None,
) -> OrderEvent:
    """Cria um evento de tracking para o pedido"""
    event = OrderEvent(
        order_id=order_id,
        status=new_status,
        status_label=STATUS_LABELS.get(new_status, new_status),
        description=description,
    )
    db.add(event)
    return event


async def fetch_address_data(
    address_data: AddressCreateByCEP,
) -> tuple[AddressFromCEP, Coordinates | None]:
    """
    Busca dados do endereço via APIs externas (ViaCEP + Nominatim).
    Faz isso ANTES de qualquer operação no banco para evitar dados órfãos.
    """
    # Busca dados do CEP
    cep_data = await fetch_address_by_cep(address_data.cep)
    
    if not cep_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CEP '{address_data.cep}' não encontrado ou inválido.",
        )
    
    street = cep_data.street or "Endereço não informado"
    
    # Tenta buscar coordenadas (não bloqueia se falhar)
    coords = await geocode_address(
        street=street,
        number=address_data.number,
        city=cep_data.city,
        state=cep_data.state,
    )
    
    # Fallback: tenta geocoding só pelo CEP
    if not coords:
        coords = await geocode_by_cep(address_data.cep)
    
    return cep_data, coords


def create_address_from_data(
    db: Session,
    address_input: AddressCreateByCEP,
    cep_data: AddressFromCEP,
    coords: Coordinates | None,
) -> Address:
    """Cria o Address no banco a partir dos dados já buscados"""
    address = Address(
        cep=cep_data.cep,
        street=cep_data.street or "Endereço não informado",
        number=address_input.number,
        complement=address_input.complement,
        city=cep_data.city,
        state=cep_data.state,
        latitude=coords.latitude if coords else None,
        longitude=coords.longitude if coords else None,
    )
    db.add(address)
    return address


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria um novo pedido com endereços de origem e destino.
    
    Os campos street, city e state são preenchidos automaticamente via ViaCEP.
    Você só precisa informar: cep, number e complement (opcional).
    """
    
    # 1️⃣ Busca dados externos ANTES de tocar no banco
    # Se falhar aqui, não há nada para rollback
    origin_cep_data, origin_coords = await fetch_address_data(order_data.origin_address)
    dest_cep_data, dest_coords = await fetch_address_data(order_data.destination_address)
    
    # 2️⃣ Transação atômica: tudo ou nada
    try:
        # Cria endereços
        origin = create_address_from_data(
            db, order_data.origin_address, origin_cep_data, origin_coords
        )
        destination = create_address_from_data(
            db, order_data.destination_address, dest_cep_data, dest_coords
        )
        
        db.flush()  # Obtém IDs dos endereços
        
        # Cria o pedido
        order = Order(
            tracking_code=generate_tracking_code(),
            status=OrderStatus.CREATED.value,
            owner_id=current_user.id,
            origin_address_id=origin.id,
            destination_address_id=destination.id,
        )
        db.add(order)
        db.flush()  # Obtém ID do pedido
        
        # Cria evento inicial de tracking
        create_order_event(
            db=db,
            order_id=order.id,
            new_status=OrderStatus.CREATED.value,
            description="Pedido registrado no sistema",
        )
        
        db.commit()
        db.refresh(order)
        
        return order
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar pedido. Tente novamente.",
        )


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


@router.get("/all", response_model=list[OrderListResponse])
def list_all_orders(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    🔐 ADMIN ONLY — Lista TODOS os pedidos do sistema.
    
    Filtros opcionais:
    - status_filter: created, in_transit, delivered, canceled
    """
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    return query.order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna detalhes de um pedido específico (dono ou admin)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )
    
    # Admin pode ver qualquer pedido, usuário só os seus
    is_admin = current_user.role == UserRole.ADMIN.value
    is_owner = order.owner_id == current_user.id
    
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este pedido.",
        )
    
    return order


# Descrições padrão para cada transição de status
STATUS_DESCRIPTIONS = {
    "in_transit": "Pedido coletado e saiu para entrega",
    "delivered": "Pedido entregue com sucesso",
    "canceled": "Pedido cancelado",
}


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza o status de um pedido e registra evento na timeline (dono ou admin)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )
    
    # Admin pode atualizar qualquer pedido, usuário só os seus
    is_admin = current_user.role == UserRole.ADMIN.value
    is_owner = order.owner_id == current_user.id
    
    if not is_admin and not is_owner:
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
    
    # Transação atômica
    try:
        order.status = new_status
        
        create_order_event(
            db=db,
            order_id=order.id,
            new_status=new_status,
            description=STATUS_DESCRIPTIONS.get(new_status),
        )
        
        db.commit()
        db.refresh(order)
        
        return order
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status. Tente novamente.",
        )
