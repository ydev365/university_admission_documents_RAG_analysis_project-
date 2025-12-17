from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/setuek_rag"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()
