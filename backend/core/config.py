"""
core/config.py — Configuración centralizada del proyecto.

Usa pydantic-settings para cargar variables desde el .env.
Un ÚNICO objeto `settings` importable desde cualquier módulo:

    from core.config import settings
    print(settings.REDIS_URL)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Todas las variables de configuración del backend.
    Se cargan automáticamente del archivo .env o de variables de entorno del sistema.
    """

    # ─── Redis (Celery broker + backend) ───
    REDIS_URL: str = "redis://redis:6379/0"

    # ─── Qdrant (Vector Database) ───
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "corporate_docs"

    # ─── Embeddings ───
    EMBEDDING_PROVIDER: str = "sentence-transformers"  # "sentence-transformers" | "openai"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384  # Dimensión del vector (384 para MiniLM)

    # ─── OpenAI / LLM ───
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # ─── LLM provider (local | openai | gemini | claude) ───
    LLM_PROVIDER: str = "local"
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    GEMINI_LLM_MODEL: str = "gemini-2.5-flash"
    CLAUDE_LLM_MODEL: str = "claude-3-haiku-20240307"

    # ─── Procesamiento de documentos ───
    CHUNK_SIZE: int = 1000      # Tamaño de cada fragmento (en caracteres)
    CHUNK_OVERLAP: int = 200    # Solapamiento entre fragmentos
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ignorar vars no declaradas en el modelo


# Singleton — se importa desde cualquier módulo
settings = Settings()
