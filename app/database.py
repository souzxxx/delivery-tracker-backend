from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engine de conexão com o Postgres
engine = create_engine(settings.DATABASE_URL, future=True)

# Sessão para usar nas rotas/serviços
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para declarar os models
Base = declarative_base()
