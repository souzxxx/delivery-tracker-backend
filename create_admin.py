"""
Script para criar o primeiro usuário administrador.
Execute: python create_admin.py
"""
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def create_admin():
    db = SessionLocal()
    
    try:
        # Verifica se já existe um admin
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if existing_admin:
            print(f"⚠️  Já existe um administrador: {existing_admin.email}")
            return
        
        # Dados do admin (altere conforme necessário)
        admin_email = "admin@delivery.com"
        admin_password = "admin123"  # Troque por uma senha forte em produção!
        admin_name = "Administrador"
        
        # Verifica se o email já está em uso
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            # Promove usuário existente a admin
            existing_user.role = UserRole.ADMIN.value
            db.commit()
            print(f"✅ Usuário {admin_email} promovido a administrador!")
            return
        
        # Cria o admin
        admin = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name=admin_name,
            role=UserRole.ADMIN.value,
        )
        
        db.add(admin)
        db.commit()
        print(f"✅ Administrador criado com sucesso!")
        print(f"   Email: {admin_email}")
        print(f"   Senha: {admin_password}")
        print(f"   ⚠️  Troque a senha em produção!")
        
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()

