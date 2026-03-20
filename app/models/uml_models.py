from pydantic import BaseModel
from typing import List, Optional

# ─── Modelos para atributos y métodos de clases ───────────────────────────────

class Attribute(BaseModel):
    """Representa un atributo de una clase UML."""
    name: str
    type: str
    visibility: str  # "public", "private", "protected"

class Method(BaseModel):
    """Representa un método de una clase UML."""
    name: str
    returnType: str
    visibility: str  # "public", "private", "protected"

class UMLClass(BaseModel):
    """Representa una clase completa con atributos y métodos."""
    name: str
    attributes: List[Attribute] = []
    methods: List[Method] = []

class Relationship(BaseModel):
    """Representa una relación entre dos clases."""
    type: str          # "association", "inheritance", "composition", "aggregation"
    from_: str         # Clase origen (usamos from_ porque "from" es palabra reservada)
    to: str            # Clase destino
    multiplicityFrom: Optional[str] = None  # Ej: "1"
    multiplicityTo: Optional[str] = None    # Ej: "*"

    # Permite que el JSON use "from" mapeado a "from_"
    model_config = {
        "populate_by_name": True,
        "alias_generator": lambda field: "from" if field == "from_" else field
    }

# ─── Modelo principal del request ─────────────────────────────────────────────

class UMLRequest(BaseModel):
    """JSON completo que recibe el endpoint /uml/generate."""
    diagramType: str          # "classDiagram", "sequenceDiagram", etc.
    classes: List[UMLClass] = []
    relationships: List[Relationship] = []

# ─── Modelo de la respuesta ───────────────────────────────────────────────────

class UMLResponse(BaseModel):
    """Respuesta con la URL de la imagen generada."""
    image_url: str
    plantuml_code: str        # Devolvemos también el código para debugging
