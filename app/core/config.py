from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Delivery Tracker API"
    API_V1_STR: str = "/api/v1"

    # 🗄️ Banco de dados
    DATABASE_URL: str

    # 🔐 Configs de segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1h


settings = Settings()
