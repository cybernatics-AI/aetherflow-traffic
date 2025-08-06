"""
Configuration management for AetherFlow Backend
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    API_VERSION: str = Field(default="v1", env="API_VERSION")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./aetherflow.db", env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Hedera Network Configuration
    HEDERA_NETWORK: str = Field(default="testnet", env="HEDERA_NETWORK")
    HEDERA_ACCOUNT_ID: str = Field(env="HEDERA_ACCOUNT_ID")
    HEDERA_PRIVATE_KEY: str = Field(env="HEDERA_PRIVATE_KEY")
    HEDERA_PUBLIC_KEY: Optional[str] = Field(default=None, env="HEDERA_PUBLIC_KEY")
    
    # HCS Topics Configuration
    HCS_REGISTRY_TOPIC_ID: Optional[str] = Field(default=None, env="HCS_REGISTRY_TOPIC_ID")
    HCS_INBOUND_TOPIC_ID: Optional[str] = Field(default=None, env="HCS_INBOUND_TOPIC_ID")
    HCS_OUTBOUND_TOPIC_ID: Optional[str] = Field(default=None, env="HCS_OUTBOUND_TOPIC_ID")
    HCS_TTL: int = Field(default=60, env="HCS_TTL")
    
    # HTS Token Configuration
    AETHER_TOKEN_ID: Optional[str] = Field(default=None, env="AETHER_TOKEN_ID")
    TRAFFIC_NFT_TOKEN_ID: Optional[str] = Field(default=None, env="TRAFFIC_NFT_TOKEN_ID")
    
    # AI/ML Configuration
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama3-8b-8192", env="GROQ_MODEL")
    GROQ_MAX_TOKENS: int = Field(default=4096, env="GROQ_MAX_TOKENS")
    GROQ_TEMPERATURE: float = Field(default=0.1, env="GROQ_TEMPERATURE")
    TENSORFLOW_SERVING_URL: str = Field(default="http://localhost:8501", env="TENSORFLOW_SERVING_URL")
    FEDERATED_LEARNING_ENABLED: bool = Field(default=True, env="FEDERATED_LEARNING_ENABLED")
    
    # Security Configuration
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External APIs
    OPENWEATHERMAP_API_KEY: Optional[str] = Field(default=None, env="OPENWEATHERMAP_API_KEY")
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="aetherflow.log", env="LOG_FILE")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
