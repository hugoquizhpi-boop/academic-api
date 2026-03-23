# 🎓 API Académica

API REST construida con **FastAPI** que provee tres herramientas para plataformas académicas.

**URL base (producción):** `https://academic-api-888p.onrender.com`  
**Documentación interactiva:** `https://academic-api-888p.onrender.com/docs`

---

## ¿Qué hace esta API?

| Endpoint | Descripción |
|---|---|
| `POST /uml/generate` | Genera una imagen PNG de un diagrama UML desde JSON |
| `POST /documents/generate` | Convierte texto a PDF, Word o PowerPoint (descarga directa) |
| `POST /citations/graph` | Genera un grafo visual de citaciones a partir de un DOI |

---

## Endpoints

### 📊 `POST /uml/generate`

Recibe clases y relaciones, devuelve la URL de la imagen generada.

**Request:**
```json
{
  "diagramType": "classDiagram",
  "classes": [
    {
      "name": "Usuario",
      "attributes": [
        { "name": "id",     "type": "int",    "visibility": "public" },
        { "name": "nombre", "type": "string", "visibility": "private" }
      ],
      "methods": [
        { "name": "login()", "returnType": "void", "visibility": "public" }
      ]
    }
  ],
  "relationships": [
    {
      "type": "association",
      "from": "Usuario",
      "to": "Pedido",
      "multiplicityFrom": "1",
      "multiplicityTo": "*"
    }
  ]
}
```

**Response `200`:**
```json
{
  "image_url": "https://academic-api-888p.onrender.com/media/uml/diagram_abc123.png",
  "plantuml_code": "@startuml\nclass Usuario {\n  +id : int\n}\n@enduml"
}
```

**Valores válidos:**

- `visibility`: `"public"` → `+` / `"private"` → `-` / `"protected"` → `#`
- `type` (relación): `"association"` · `"inheritance"` · `"composition"` · `"aggregation"` · `"dependency"` · `"realization"`

---

### 📄 `POST /documents/generate`

Genera un documento y lo devuelve como **archivo descargable**.

**Request:**
```json
{
  "title": "Informe de Sistemas",
  "format": "pdf",
  "text": "Introducción\n\nContenido del primer párrafo.\n\nConclusión\n\nResumen final."
}
```

**Valores de `format`:** `"pdf"` · `"word"` · `"ppt"`

> Usa doble salto de línea `\n\n` para separar secciones. En PPT cada sección se convierte en un slide.

**Response:** El archivo se descarga directamente (no es JSON).

---

### 🔗 `POST /citations/graph`

Busca un paper por DOI en OpenAlex y genera un grafo PNG con los papers que lo citan.

**Request:**
```json
{
  "doi": "10.1038/s41586-021-03819-2",
  "max_nodes": 20
}
```

**Response `200`:**
```json
{
  "image_url": "https://academic-api-888p.onrender.com/media/graphs/graph_xyz789.png",
  "total_citations": 18,
  "paper_title": "Highly accurate protein structure prediction with AlphaFold"
}
```

**Response `404`:** DOI no encontrado en OpenAlex.

---

## Cómo usar desde tu código

### JavaScript / Fetch

```javascript
// Generar diagrama UML
const response = await fetch('https://academic-api-888p.onrender.com/uml/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    diagramType: 'classDiagram',
    classes: [{ name: 'Producto', attributes: [], methods: [] }],
    relationships: []
  })
});
const data = await response.json();
console.log(data.image_url); // URL de la imagen generada
```

```javascript
// Descargar documento PDF
const response = await fetch('https://academic-api-888p.onrender.com/documents/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Mi Reporte',
    format: 'pdf',
    text: 'Introducción\n\nContenido principal.'
  })
});
const blob = await response.blob();
const url = URL.createObjectURL(blob);
// Mostrar el PDF o forzar descarga
```

```javascript
// Grafo de citaciones
const response = await fetch('https://academic-api-888p.onrender.com/citations/graph', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    doi: '10.1038/nature12373',
    max_nodes: 15
  })
});
const data = await response.json();
console.log(data.image_url); // URL del grafo generado
```

### Python / requests

```python
import requests

# Grafo de citaciones
r = requests.post(
    'https://academic-api-888p.onrender.com/citations/graph',
    json={'doi': '10.1038/nature12373', 'max_nodes': 15}
)
print(r.json()['image_url'])
```

---

## Correr localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/hugoquizhpi-boop/academic-api.git
cd academic-api

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

Servidor disponible en `http://localhost:8000`  
Documentación interactiva en `http://localhost:8000/docs`

---

## Notas

- Las imágenes y documentos generados se sirven desde `/media/` y son accesibles por URL directa.
- El servidor en Render puede tardar ~30 segundos en responder la primera petición si estuvo inactivo (plan gratuito).
- La API de citaciones usa [OpenAlex](https://openalex.org/) — no requiere API key.