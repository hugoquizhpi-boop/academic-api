"""
Punto de entrada principal de la API académica.

Para ejecutar:
    uvicorn app.main:app --reload

Para producción:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Importar todos los routers
from app.routers import uml, documents, citations

# ── Crear la aplicación ───────────────────────────────────────────────────────
app = FastAPI(
    title="API Académica",
    description="""
## API para herramientas académicas

Esta API proporciona tres funcionalidades principales:

### 📊 Diagramas UML
Genera diagramas UML desde JSON estructurado usando PlantUML.

### 📄 Generación de Documentos
Convierte texto a documentos Word, PDF o PowerPoint.

### 🔗 Grafos de Citaciones
Genera grafos visuales de citaciones académicas desde un DOI.
    """,
    version="1.0.0",
)

# ── CORS (permite que el frontend pueda llamar a esta API) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # En producción, reemplazar con tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Crear directorios de media si no existen ──────────────────────────────────
os.makedirs("media/uml",       exist_ok=True)
os.makedirs("media/documents", exist_ok=True)
os.makedirs("media/graphs",    exist_ok=True)

# ── Servir archivos estáticos (imágenes y documentos generados) ───────────────
# Esto hace que http://localhost:8000/media/uml/imagen.png funcione
app.mount("/media", StaticFiles(directory="media"), name="media")

# ── Registrar routers ─────────────────────────────────────────────────────────
app.include_router(uml.router)
app.include_router(documents.router)
app.include_router(citations.router)


# ── Endpoint de salud (para verificar que el servidor funciona) ───────────────
@app.get("/", tags=["Estado"])
async def root():
    return {
        "status": "ok",
        "message": "API Académica funcionando correctamente",
        "docs": "/docs",          # Swagger UI
        "redoc": "/redoc",        # ReDoc (documentación alternativa)
    }


@app.get("/health", tags=["Estado"])
async def health_check():
    return {"status": "healthy"}
