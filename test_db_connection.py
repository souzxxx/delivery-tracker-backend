from sqlalchemy import text
from app.database import engine

def main():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            print("Conexão OK! Resultado:", result.scalar())
    except Exception as e:
        print("ERRO ao conectar no banco:")
        print(e)

if __name__ == "__main__":
    main()
