import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "GDH Auth Demo"
    ENVIRONMENT: str = "production"
    SERVER_HOST: str = "greenserver"
    CONTAINER_NAME: str = "gdh-auth-demo-prod"
    NEXO_URL: str = "http://100.127.143.52:8000"
    NEXO_API_KEY: str = "demo_key"
    SYSTEM_SLUG: str = "gdh-auth-demo"

    class Config:
        env_file = ".env"

settings = Settings()
