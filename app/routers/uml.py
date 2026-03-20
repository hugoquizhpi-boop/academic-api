"""
Router UML: define los endpoints HTTP relacionados con diagramas UML.

El router es solo el "portero": recibe el request, lo valida y delega
al servicio. No contiene lógica de negocio.
"""

from fastapi import APIRouter, Request, HTTPException
from app.models.uml_models import UMLRequest, UMLResponse
from app.services.uml_service import generate_uml_diagram

# Creamos el router con prefijo /uml
router = APIRouter(prefix="/uml", tags=["UML"])


@router.post(
    "/generate",
    response_model=UMLResponse,
    summary="Genera un diagrama UML desde JSON",
    description="""
Recibe un JSON con clases y relaciones, genera código PlantUML,
obtiene la imagen PNG del servidor de PlantUML y devuelve la URL.
    """
)
async def generate_uml(request_data: UMLRequest, request: Request):
    """
    Endpoint principal para generación de diagramas UML.

    - **diagramType**: Tipo de diagrama (classDiagram, etc.)
    - **classes**: Lista de clases con atributos y métodos
    - **relationships**: Lista de relaciones entre clases
    """
    try:
        # Obtener URL base del servidor (ej: "http://localhost:8000")
        base_url = str(request.base_url).rstrip("/")

        result = await generate_uml_diagram(request_data, base_url)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando diagrama UML: {str(e)}"
        )
