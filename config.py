"""
Configuration management for AI Viva Examiner.
All settings are loaded from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    groq_api_key: str
    openai_api_key: str  # Still needed for embeddings
    
    # LLM Provider
    llm_provider: str = "groq"  # groq or openai
    
    # LLM Configuration
    llm_model: str = "llama-3.1-70b-versatile"  # Groq models: llama-3.1-70b-versatile, mixtral-8x7b-32768
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    
    # Vector Store Configuration
    vector_store_type: str = "faiss"
    vector_store_path: Path = Path("./data/vector_store")
    
    # File Upload Configuration
    max_file_size_mb: int = 50
    allowed_file_types: str = "application/pdf"
    
    # Question Generation Configuration
    num_questions: int = 5
    question_generation_timeout: int = 60
    
    # Answer Evaluation Configuration
    evaluation_timeout: int = 10
    min_score: int = 1
    max_score: int = 10
    
    # Session Configuration
    session_storage_type: str = "sqlite"
    session_db_path: Path = Path("./data/sessions.db")
    
    # Performance Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_retries: int = 3
    retry_delay: int = 1
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Path = Path("./logs/app.log")
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.vector_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
