from datetime import datetime

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Schema for API settings."""

    db_host: str = "localhost"
    db_user: str
    db_password: str
    db_name: str
    db_port: int
    secret_key: str
    oauth2_algorithm: str
    access_token_expire_minutes: int
    access_token_duration: datetime | None = None

    class Config:
        env_file = ".env"


settings = Settings()
