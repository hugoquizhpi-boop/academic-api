"""
Servicio de citaciones: consulta OpenAlex para obtener citas de un paper
y genera un grafo visual usando networkx + matplotlib.

OpenAlex es una API académica gratuita y sin necesidad de API key.
Documentación: https://docs.openalex.org/
"""

import os
import uuid
import httpx
from app.models.citation_models import CitationRequest, CitationResponse
from app.utils.graph_generator import build_citation_graph

MEDIA_GRAPHS_DIR = "media/graphs"

# URL base de la API de OpenAlex
OPENALEX_API = "https://api.openalex.org"


async def _fetch_paper_data(doi: str) -> dict:
    """
    Busca un paper en OpenAlex usando su DOI.

    OpenAlex acepta DOIs en formato: https://doi.org/10.xxxx/xxxxx
    o directamente: 10.xxxx/xxxxx
    """
    # Normalizar el DOI (eliminar prefijo si ya lo tiene)
    clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")

    url = f"{OPENALEX_API}/works/https://doi.org/{clean_doi}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            url,
            headers={"User-Agent": "AcademicWebApp/1.0 (mailto:tu_email@ejemplo.com)"}
        )

    if response.status_code == 404:
        raise ValueError(f"No se encontró ningún paper con DOI: {doi}")

    if response.status_code != 200:
        raise Exception(f"Error al consultar OpenAlex: {response.status_code}")

    return response.json()


async def _fetch_references(openalex_id: str, max_nodes: int) -> list:
    """
    Obtiene los trabajos que cita el paper (sus referencias bibliográficas).

    En OpenAlex esto se llama "referenced_works" (lo que el paper cita)
    vs "cited_by" (quién cita al paper).
    """
    # Buscar trabajos que citan a este paper
    url = f"{OPENALEX_API}/works"

    params = {
        "filter": f"cites:{openalex_id}",
        "per-page": min(max_nodes, 50),
        "select": "id,title,doi,publication_year"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            url,
            params=params,
            headers={"User-Agent": "AcademicWebApp/1.0 (mailto:tu_email@ejemplo.com)"}
        )

    if response.status_code != 200:
        return []

    data = response.json()
    results = data.get("results", [])

    # Convertir al formato esperado por graph_generator
    citations = []
    for work in results:
        citations.append({
            "title": work.get("title") or "Sin título",
            "doi":   work.get("doi") or "",
            "year":  work.get("publication_year") or ""
        })

    return citations


async def generate_citation_graph(
    request: CitationRequest,
    base_url: str
) -> CitationResponse:
    """
    Orquesta el proceso completo:
    1. Busca el paper en OpenAlex por DOI
    2. Obtiene sus citas
    3. Genera el grafo visual
    4. Guarda la imagen y retorna la URL

    Args:
        request: CitationRequest con el DOI
        base_url: URL base del servidor

    Returns:
        CitationResponse con image_url, total_citations y paper_title
    """
    os.makedirs(MEDIA_GRAPHS_DIR, exist_ok=True)

    # Paso 1: Obtener datos del paper raíz
    paper_data = await _fetch_paper_data(request.doi)

    paper_title = paper_data.get("title") or "Sin título"
    openalex_id = paper_data.get("id", "").split("/")[-1]  # Ej: "W2741809807"

    # Paso 2: Obtener papers que lo citan
    citations = await _fetch_references(openalex_id, request.max_nodes)

    # Si no hay citas en OpenAlex, usamos las referencias del paper
    if not citations:
        referenced_ids = paper_data.get("referenced_works", [])[:request.max_nodes]
        # Obtener títulos de los trabajos referenciados
        citations = []
        for ref_url in referenced_ids:
            ref_id = ref_url.split("/")[-1]
            citations.append({
                "title": f"Trabajo referenciado {ref_id[:8]}",
                "doi": "",
                "year": ""
            })

    # Paso 3: Generar imagen del grafo
    filename = f"graph_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(MEDIA_GRAPHS_DIR, filename)

    total = build_citation_graph(
        root_title=paper_title,
        citations=citations,
        output_path=output_path,
        max_nodes=request.max_nodes
    )

    # Paso 4: Construir respuesta
    image_url = f"{base_url}/media/graphs/{filename}"

    return CitationResponse(
        image_url=image_url,
        total_citations=total,
        paper_title=paper_title
    )
