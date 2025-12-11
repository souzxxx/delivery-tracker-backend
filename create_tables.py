from app.database import Base, engine
from app.models import user  # importa para registrar o model no metadata

def main():
    print("Criando tabelas no banco...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    main()
