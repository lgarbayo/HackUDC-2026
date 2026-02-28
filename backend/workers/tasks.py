"""
workers/tasks.py — Tareas de Celery (el motor pesado).

Contiene la tarea `process_document` que ejecuta la pipeline completa:
  1. Extraer texto del PDF (PyMuPDF)
  2. Limpiar texto (regex)
  3. Fragmentar en chunks con solapamiento
  4. Deduplicar chunks (SHA256)
  5. Vectorizar y guardar en Qdrant

Esta tarea se ejecuta en BACKGROUND — nunca bloquea FastAPI.
Se dispara desde el endpoint POST /api/upload con:
    process_document.delay(file_path, original_filename)
"""

import logging
from workers.celery_app import celery_app
from services.document_extractor import (
    extract_document_content,
    clean_text,
    chunk_text,
    deduplicate_chunks,
)
from services.vector_db import VectorDBService
from core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="workers.tasks.process_document")
def process_document(self, file_path: str, original_filename: str) -> dict:
    """
    Pipeline completa de procesamiento de un documento.

    Args:
        self: Referencia a la tarea (bind=True) para actualizar estado.
        file_path: Ruta al archivo PDF guardado en el servidor.
        original_filename: Nombre original del archivo subido.

    Returns:
        dict con metadata del procesamiento:
          - status: "completed"
          - filename: nombre original
          - total_chunks: número de chunks insertados
          - unique_chunks: chunks tras deduplicación
    """
    try:
        # ── Paso 1: Extraer texto y metadatos ──
        self.update_state(state="PROCESSING", meta={"step": "extracting_text"})
        logger.info(f"📄 Extrayendo contenido de: {original_filename}")
        raw_text, doc_metadata = extract_document_content(file_path)
        logger.info(f"   → {len(raw_text)} caracteres extraídos. Categoría: {doc_metadata.get('category')}")

        # ── Paso 2: Limpiar ──
        self.update_state(state="PROCESSING", meta={"step": "cleaning_text"})
        logger.info("🧹 Limpiando texto...")
        cleaned_text = clean_text(raw_text)
        logger.info(f"   → {len(cleaned_text)} caracteres tras limpieza")

        # ── Paso 2b: Generar resumen con LLM (no bloqueante — best-effort) ──
        self.update_state(state="PROCESSING", meta={"step": "summarizing"})
        summary = ""
        try:
            from services.llm_service import get_llm_service
            llm = get_llm_service()
            summary = llm.summarize(cleaned_text[:5000])
            logger.info(f"📝 Resumen generado: {len(summary)} caracteres")
        except Exception as e:
            logger.warning(f"⚠️  Resumen LLM no disponible ({type(e).__name__}): {e}")

        # ── Paso 3: Fragmentar ──
        self.update_state(state="PROCESSING", meta={"step": "chunking"})
        logger.info(f"✂️  Fragmentando (size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})...")
        chunks = chunk_text(cleaned_text, size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
        logger.info(f"   → {len(chunks)} chunks generados")

        # ── Paso 4: Deduplicar ──
        self.update_state(state="PROCESSING", meta={"step": "deduplicating"})
        total_before = len(chunks)
        chunks = deduplicate_chunks(chunks)
        duplicates_removed = total_before - len(chunks)
        logger.info(f"🔍 Deduplicación: {duplicates_removed} duplicados eliminados, {len(chunks)} chunks únicos")

        # ── Paso 5: Vectorizar y guardar ──
        self.update_state(state="PROCESSING", meta={"step": "embedding_and_storing"})
        logger.info("🧠 Vectorizando e insertando en Qdrant...")

        vdb = VectorDBService()
        vdb.ensure_collection()

        # Crear metadata para cada chunk combinando los globales del doc
        metadata = []
        for i in range(len(chunks)):
            chunk_meta = {
                "source": original_filename,
                "chunk_index": i,
                "summary": summary,
            }
            # Añadir metadatos deducidos (category, file_size, extension)
            chunk_meta.update(doc_metadata)
            metadata.append(chunk_meta)

        inserted = vdb.upsert(chunks=chunks, metadata=metadata)
        logger.info(f"✅ {inserted} vectores insertados en Qdrant")

        # ── Resultado ──
        result = {
            "status": "completed",
            "filename": original_filename,
            "total_chunks": total_before,
            "unique_chunks": len(chunks),
            "duplicates_removed": duplicates_removed,
            "characters_extracted": len(raw_text),
            "characters_cleaned": len(cleaned_text),
        }

        logger.info(f"🎉 Procesamiento completado: {original_filename}")
        return result

    except Exception as e:
        logger.error(f"❌ Error procesando {original_filename}: {e}")
        # Celery marca la tarea como FAILURE automáticamente si hay excepción
        raise
