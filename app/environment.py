from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: PostgresDsn
    # SECRET_KEY: str
    # REDIS_URL: RedisDsn
    CORS_ORIGINS: list[str]
    CORS_HEADERS: list[str]


settings = Settings()  # pyright: ignore
