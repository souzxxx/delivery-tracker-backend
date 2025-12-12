from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate, UserResponse, UserRoleUpdate
from app.models.user import User
from app.services.db_service import get_db
from app.utils.security import get_password_hash
from app.services.auth_service import get_current_user, get_current_admin

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # opcional: checar se email já existe
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado.",
        )

    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),  # 👈 agora com hash
        full_name=user.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),  # Somente admin pode listar usuários
):
    return db.query(User).all()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Atualiza o role de um usuário (somente admin).
    Use para promover usuário a admin ou rebaixar admin a usuário.
    """
    # Busca o usuário
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    
    # Impede que admin remova o próprio role de admin
    if user.id == current_admin.id and role_update.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover seu próprio status de administrador.",
        )
    
    # Atualiza o role
    user.role = role_update.role.value
    db.commit()
    db.refresh(user)
    return user
