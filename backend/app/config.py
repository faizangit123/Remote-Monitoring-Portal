"""
Configuration Management
This file loads and validates all configuration settings from .env file
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):

    # Database Configuration
    DATABASE_URL: str

    
    # Security Settings - JWT Token Configuration
    SECRET_KEY: str
    
    ALGORITHM: str = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Server Configuration
    HOST: str = "0.0.0.0"
    
    PORT: int = 8000
    
    # CORS Configuration (Cross-Origin Resource Sharing)
    CORS_ORIGINS: str
    
    @property
    def cors_origins_list(self) -> List[str]:

        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

if __name__ == "__main__":
    print("Configuration loaded successfully:")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"CORS Origins: {settings.cors_origins_list}")
    print(f"Token expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")