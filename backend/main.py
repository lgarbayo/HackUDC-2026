"""
main.py — Punto de entrada de FastAPI.

Arranca la aplicación, incluye el router de rutas,
y expone un health check para verificar que el servidor está vivo.

Ejecución:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="Meiga — Asistente de Conocimiento Corporativo",
    description="Backend RAG: ingesta de PDFs, procesamiento async, búsqueda semántica.",
    version="1.0.0",
)

# CORS — permite peticiones desde cualquier frontend (desarrollo)
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
