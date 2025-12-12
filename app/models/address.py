from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados do endereço
    cep = Column(String(9), nullable=False)  # 00000-000
    street = Column(String(255), nullable=False)
    number = Column(String(20), nullable=False)
    complement = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)  # UF
    
    # Coordenadas (opcional por enquanto, Nominatim depois)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

