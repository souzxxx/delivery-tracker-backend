from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Delivery Tracker API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+psycopg2://delivery_user:delivery_password@localhost:5432/delivery_db"
    )

    class Config:
        case_sensitive = True

settings = Settings()
