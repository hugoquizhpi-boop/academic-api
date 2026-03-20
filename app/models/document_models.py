from pydantic import BaseModel
from typing import Literal

class DocumentRequest(BaseModel):
    """JSON que recibe el endpoint /documents/generate."""
    text: str
    format: Literal["pdf", "word", "ppt"]  # Solo estos 3 formatos aceptados
    title: str = "Documento Generado"       # Título opcional con valor por defecto
