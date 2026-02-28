"""
api/routes.py — Endpoints de la API.

Tres endpoints:
  POST /api/upload       → Sube un PDF, dispara procesamiento async
  GET  /api/search       → Búsqueda semántica sobre los documentos
  GET  /api/status/{id}  → Estado de una tarea de procesamiento
"""

import os
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from workers.tasks import process_document
from services.vector_db import VectorDBService
from core.config import settings
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════
#  POST /api/upload — Ingesta de documentos
# ═══════════════════════════════════════════════════════════════

@router.post("/upload", tags=["Ingesta"])
async def upload_document(file: UploadFile = File(...)):
    """
    Sube un PDF para procesamiento asíncrono.

    1. Valida que sea un PDF
    2. Guarda el archivo en disco
    3. Dispara la tarea de Celery (NO bloquea)
    4. Devuelve HTTP 202 con el task_id para tracking

    Returns:
        202 Accepted con task_id y filename.
    """
    # Validar tipo de archivo
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF."
        )

    # Crear directorio de uploads si no existe
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Guardar archivo en disco
    file_path = upload_dir / file.filename
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"📁 Archivo guardado: {file_path} ({len(content)} bytes)")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error guardando el archivo: {e}"
        )

    # Disparar tarea de Celery (async, no bloquea FastAPI)
    task = process_document.delay(str(file_path), file.filename)

    logger.info(f"🚀 Tarea disparada: {task.id} para {file.filename}")

    return JSONResponse(
        status_code=202,
        content={
            "message": "Documento recibido. Procesamiento en curso.",
            "task_id": task.id,
            "filename": file.filename,
        }
    )


# ═══════════════════════════════════════════════════════════════
#  GET /api/status/{task_id} — Estado de la tarea
# ═══════════════════════════════════════════════════════════════

@router.get("/status/{task_id}", tags=["Ingesta"])
async def get_task_status(task_id: str):
    """
    Consulta el estado de una tarea de procesamiento.

    Estados posibles:
      - PENDING: La tarea está en la cola, esperando un worker.
      - PROCESSING: El worker está procesándola (con detalle del paso actual).
      - SUCCESS: Procesamiento completado exitosamente.
      - FAILURE: Error durante el procesamiento.

    Returns:
        Estado actual + metadata del resultado si completó.
    """
    result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    # Si está en proceso, incluir info del paso actual
    if result.state == "PROCESSING":
        response["detail"] = result.info

    # Si completó, incluir el resultado
    elif result.state == "SUCCESS":
        response["result"] = result.result

    # Si falló, incluir el error
    elif result.state == "FAILURE":
        response["error"] = str(result.result)

    return response


# ═══════════════════════════════════════════════════════════════
#  GET /api/search — Búsqueda semántica
# ═══════════════════════════════════════════════════════════════

@router.get("/search", tags=["Búsqueda"])
async def search_documents(
    q: str = Query(..., min_length=1, description="Texto de búsqueda"),
    top_k: int = Query(5, ge=1, le=20, description="Número de resultados"),
):
    """
    Búsqueda semántica sobre los documentos indexados.

    Vectoriza la query, busca en Qdrant por similitud coseno,
    y devuelve los top_k chunks más relevantes.

    Returns:
        Lista de resultados con: text, score, source.
    """
    try:
        vdb = VectorDBService()
        results = vdb.search(query=q, top_k=top_k)

        return {
            "query": q,
            "top_k": top_k,
            "results": results,
        }

    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error realizando la búsqueda: {e}"
        )
