"""
Router de documentos: endpoints para generar .docx, .pdf y .pptx.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.document_models import DocumentRequest
from app.services.document_service import generate_document

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.post(
    "/generate",
    summary="Genera un documento desde texto",
    description="""
Recibe texto plano y un formato, genera el documento y lo devuelve
como archivo descargable.

Formatos soportados: **pdf**, **word**, **ppt**
    """
)
async def create_document(request_data: DocumentRequest):
    """
    Genera y descarga un documento.

    - **text**: Contenido del documento (usa doble salto de línea para separar secciones)
    - **format**: "pdf", "word" o "ppt"
    - **title**: Título del documento (opcional)
    """
    try:
        file_path, media_type = await generate_document(request_data)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error: archivo no generado")

        filename = os.path.basename(file_path)

        # FileResponse envía el archivo como descarga al cliente
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando documento: {str(e)}"
        )
