from pydantic import BaseModel

class CitationRequest(BaseModel):
    """JSON que recibe el endpoint /citations/graph."""
    doi: str          # Ej: "10.1038/nature12373"
    depth: int = 1    # Qué tan profundo buscar (1 = solo citas directas)
    max_nodes: int = 20  # Límite de nodos para no sobrecargar el grafo

class CitationResponse(BaseModel):
    """Respuesta con la URL del grafo generado."""
    image_url: str
    total_citations: int
    paper_title: str
