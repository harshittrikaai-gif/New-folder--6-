"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "Trika AI"
    debug: bool = False
    
    # API
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    supported_models: list[str] = [
        "gpt-4-turbo-preview", 
        "gpt-3.5-turbo", 
        "gpt-4",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229"
    ]
    
    # Vector Store
    vector_store_provider: str = "pinecone"  # chroma, pinecone
    
    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "trika_documents"
    
    # Pinecone
    pinecone_api_key: str = ""
    pinecone_env: str = ""
    pinecone_index: str = "trika-index"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
