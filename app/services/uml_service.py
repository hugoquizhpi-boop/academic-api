"""
Servicio UML: contiene toda la lógica de negocio para generar diagramas.

El router solo recibe y valida el request, luego llama a este servicio.
El servicio hace el trabajo real: convertir, generar imagen, guardar.
"""

import uuid
import os
from app.models.uml_models import UMLRequest, UMLResponse
from app.utils.plantuml import json_to_plantuml, generate_plantuml_image

# Directorio donde se guardan las imágenes generadas
MEDIA_UML_DIR = "media/uml"


async def generate_uml_diagram(request: UMLRequest, base_url: str) -> UMLResponse:
    """
    Orquesta todo el proceso de generación UML:
    1. Convierte el JSON a código PlantUML
    2. Genera la imagen llamando al servidor de PlantUML
    3. Guarda la imagen en /media/uml/
    4. Retorna la URL pública

    Args:
        request: El objeto UMLRequest con clases y relaciones
        base_url: URL base del servidor (ej: "http://localhost:8000")

    Returns:
        UMLResponse con image_url y plantuml_code
    """
    # Paso 1: Convertir JSON → código PlantUML
    plantuml_code = json_to_plantuml(request)

    # Paso 2: Crear nombre único para el archivo
    filename = f"diagram_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(MEDIA_UML_DIR, filename)

    # Asegurarse de que el directorio existe
    os.makedirs(MEDIA_UML_DIR, exist_ok=True)

    # Paso 3: Generar imagen (llama al servidor público de PlantUML)
    success = await generate_plantuml_image(plantuml_code, output_path)

    if not success:
        raise Exception("No se pudo generar la imagen desde el servidor PlantUML")

    # Paso 4: Construir URL pública
    image_url = f"{base_url}/media/uml/{filename}"

    return UMLResponse(
        image_url=image_url,
        plantuml_code=plantuml_code
    )
