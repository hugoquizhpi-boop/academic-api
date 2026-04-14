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

## Tipos de diagrama soportados

### Diagrama de clases (`diagramType: "class"`)
```json
{
  "diagramType": "class",
  "classes": [
    {
      "name": "Usuario",
      "attributes": [
        {"name": "id", "type": "String", "visibility": "private"},
        {"name": "nombre", "type": "String", "visibility": "private"}
      ],
      "methods": [
        {"name": "autenticar", "returnType": "boolean", "visibility": "public"}
      ]
    }
  ],
  "relationships": [
    {"from": "Usuario", "to": "Rol", "type": "association", "label": "tiene"}
  ]
}
```

### Diagrama de casos de uso (`diagramType: "usecase"`)
Los elementos en `classes` que aparecen como **origen** en las relaciones se tratan como **actores**.
Los elementos que aparecen como **destino** se tratan como **casos de uso**.

```json
{
  "diagramType": "usecase",
  "classes": [
    {"name": "Usuario", "attributes": [], "methods": []},
    {"name": "Administrador", "attributes": [], "methods": []},
    {"name": "Iniciar sesion", "attributes": [], "methods": []},
    {"name": "Registrarse", "attributes": [], "methods": []},
    {"name": "Gestionar usuarios", "attributes": [], "methods": []}
  ],
  "relationships": [
    {"from": "Usuario", "to": "Iniciar sesion", "type": "association", "label": ""},
    {"from": "Usuario", "to": "Registrarse", "type": "association", "label": ""},
    {"from": "Administrador", "to": "Iniciar sesion", "type": "association", "label": ""},
    {"from": "Administrador", "to": "Gestionar usuarios", "type": "association", "label": ""}
  ]
}
```
    """
)
async def generate_uml(request_data: UMLRequest, request: Request):
    """
    Endpoint principal para generación de diagramas UML.

    - **diagramType**: Tipo de diagrama: `class` o `usecase`
    - **classes**: Lista de clases/actores/casos de uso
    - **relationships**: Lista de relaciones entre elementos
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