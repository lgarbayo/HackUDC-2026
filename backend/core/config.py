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
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384  # Dimensión del vector (384 para MiniLM, 1536 para OpenAI)

    # ─── OpenAI (solo si EMBEDDING_PROVIDER=openai) ───
    OPENAI_API_KEY: str = ""

    # ─── Procesamiento de documentos ───
    CHUNK_SIZE: int = 1000      # Tamaño de cada fragmento (en caracteres)
    CHUNK_OVERLAP: int = 200    # Solapamiento entre fragmentos
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton — se importa desde cualquier módulo
settings = Settings()
