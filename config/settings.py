"""
Settings - Application configuration using pydantic
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Review Generator"
    debug: bool = Field(default=False)
    db_echo: bool = Field(default=False)
    
    # Database
    database_url: str = Field(default="sqlite:///review_generator.db")
    
    # API Keys
    openai_api_key: str = Field(default="")
    mistral_api_key: str = Field(default="")
    perplexity_api_key: str = Field(default="")
    deepseek_api_key: str = Field(default="")
    
    # UI Settings
    window_width: int = Field(default=1200)
    window_height: int = Field(default=800)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

