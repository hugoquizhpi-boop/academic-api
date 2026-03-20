"""
Router de citaciones: endpoints para generar grafos de citas desde DOI.
"""

from fastapi import APIRouter, Request, HTTPException
from app.models.citation_models import CitationRequest, CitationResponse
from app.services.citation_service import generate_citation_graph

router = APIRouter(prefix="/citations", tags=["Citaciones"])


@router.post(
    "/graph",
    response_model=CitationResponse,
    summary="Genera un grafo de citas desde un DOI",
    description="""
Recibe un DOI, consulta OpenAlex para obtener papers que lo citan,
genera un grafo visual y devuelve la URL de la imagen.
    """
)
async def get_citation_graph(request_data: CitationRequest, request: Request):
    """
    Genera grafo de citaciones para un paper.

    - **doi**: DOI del paper (ej: "10.1038/nature12373")
    - **max_nodes**: Máximo de papers a mostrar en el grafo (default: 20)
    """
    try:
        base_url = str(request.base_url).rstrip("/")
        result = await generate_citation_graph(request_data, base_url)
        return result

    except ValueError as e:
        # Error esperado (ej: DOI no encontrado)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando grafo de citas: {str(e)}"
        )
