"""
main.py — Punto de entrada de FastAPI.

Arranca la aplicación, incluye el router de rutas,
sirve el frontend estático, y expone un health check.

Ejecución:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router
from services.vector_db import VectorDBService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-cargar el modelo de ML en memoria RAM al arrancar el servidor
    # para que la primera búsqueda no tarde 10 segundos.
    _ = VectorDBService()
    yield
    # Lógica de apagado (opcional)

app = FastAPI(
    title="Meiga — Asistente de Conocimiento Corporativo",
    description="Backend RAG: ingesta de PDFs, procesamiento async, búsqueda semántica.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permite peticiones desde el frontend (mismo origen + desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica que el servidor FastAPI está vivo."""
    return {"status": "ok", "service": "meiga-backend"}


# ── Frontend estático ──────────────────────────────────────────
FRONTEND_PATH = "/app/frontend/index.html"
FRONTEND_ASSETS_PATH = "/app/frontend/assets"

# Serve static assets (SVG, CSS, JS, images, etc.)
if os.path.isdir(FRONTEND_ASSETS_PATH):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_PATH), name="assets")

@app.get("/", tags=["Frontend"])
async def serve_frontend():
    """Sirve el frontend estático (index.html)."""
    if os.path.isfile(FRONTEND_PATH):
        return FileResponse(FRONTEND_PATH, media_type="text/html")
    return {"error": "Frontend no encontrado. Monta el volumen frontend/ en Docker."}
