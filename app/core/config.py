from typing import List
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate API"
    PROJECT_DESCRIPTION: str = "Real Estate API for managing properties, users, and transactions."
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    SECRET_KEY: SecretStr
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_CORS_ORIGINS: List[str] = ['http://localhost:8000']

    OTP_EXPIRE_MINUTES: int = 2
    OTP_LENGTH: int = 6

    ESKIZ_EMAIL: str
    ESKIZ_PASSWORD: SecretStr

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str = 'us-east-1'
    AWS_S3_BUCKET_NAME: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
