from typing import List
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Real Estate API"
    PROJECT_DESCRIPTION: str = "Real Estate API for managing properties, users, and transactions."
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Authentication
    SECRET_KEY: SecretStr
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ['http://localhost:8000']

    # OTP
    OTP_EXPIRE_MINUTES: int = 2
    OTP_LENGTH: int = 6

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
