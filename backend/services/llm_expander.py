"""
services/llm_expander.py — Expansión de consultas usando el proveedor LLM global.

Delega en get_llm_service() para que la expansión de búsqueda descriptiva
utilice el mismo proveedor configurado en todo el sistema (local, OpenAI,
Gemini o Claude), manteniendo un servicio monolítico coherente.
"""

import logging
import asyncio

logger = logging.getLogger(__name__)


async def expand_query_async(user_query: str, max_keywords: int = 5) -> str:
    """
    Expande una consulta de búsqueda extrayendo palabras clave relevantes.
    Utiliza el proveedor LLM activo en el sistema (LLM_PROVIDER).
    """
    from services.llm_service import get_llm_service
    llm = get_llm_service()
    return await asyncio.to_thread(llm.expand_keywords, user_query)
