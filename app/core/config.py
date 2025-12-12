from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Delivery Tracker API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+psycopg2://delivery_user:delivery_password@localhost:5432/delivery_db"
    )

    # 🔐 Configs de segurança
    SECRET_KEY: str = "muda-essa-string-para-uma-bem-grande-e-secreta"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1h

    class Config:
        case_sensitive = True

settings = Settings()
