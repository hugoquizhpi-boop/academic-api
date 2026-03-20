# 🎓 API Académica — Backend FastAPI

Backend modular para una plataforma académica con tres funcionalidades principales:
generación de diagramas UML, documentos (PDF/Word/PPT) y grafos de citaciones.

---

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                 ← Punto de entrada, configuración global
│   ├── routers/
│   │   ├── uml.py              ← Endpoints /uml/...
│   │   ├── documents.py        ← Endpoints /documents/...
│   │   └── citations.py        ← Endpoints /citations/...
│   ├── services/
│   │   ├── uml_service.py      ← Lógica de generación UML
│   │   ├── document_service.py ← Lógica de documentos
│   │   └── citation_service.py ← Lógica de citaciones + OpenAlex
│   ├── models/
│   │   ├── uml_models.py       ← Modelos Pydantic para UML
│   │   ├── document_models.py  ← Modelos Pydantic para documentos
│   │   └── citation_models.py  ← Modelos Pydantic para citaciones
│   └── utils/
│       ├── plantuml.py         ← Conversión JSON→PlantUML + encoding
│       └── graph_generator.py  ← Generación de grafos con networkx
├── media/
│   ├── uml/                    ← Imágenes de diagramas generadas
│   ├── documents/              ← Documentos generados
│   └── graphs/                 ← Imágenes de grafos generadas
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación y Ejecución

### 1. Clonar y crear entorno virtual

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Mac/Linux
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor

```bash
# Desde la carpeta /backend
uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

### 4. Ver la documentación interactiva

- **Swagger UI**: http://localhost:8000/docs  ← Puedes probar los endpoints aquí
- **ReDoc**:      http://localhost:8000/redoc

---

## 🔌 Endpoints

### 📊 UML — `POST /uml/generate`

Genera una imagen PNG de un diagrama UML a partir de un JSON.

**Request:**
```json
{
  "diagramType": "classDiagram",
  "classes": [
    {
      "name": "Usuario",
      "attributes": [
        {"name": "id",     "type": "int",    "visibility": "public"},
        {"name": "nombre", "type": "string", "visibility": "public"}
      ],
      "methods": [
        {"name": "login()", "returnType": "void", "visibility": "public"}
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

**Response:**
```json
{
  "image_url": "http://localhost:8000/media/uml/diagram_abc12345.png",
  "plantuml_code": "@startuml\n..."
}
```

**Tipos de visibilidad:** `public` (+), `private` (-), `protected` (#)

**Tipos de relación:** `association`, `inheritance`, `composition`, `aggregation`, `dependency`, `realization`

---

### 📄 Documentos — `POST /documents/generate`

Genera y descarga un documento desde texto plano.

**Request:**
```json
{
  "text": "Introducción\n\nEste es el contenido principal del documento.\n\nConclusión\n\nResumen final.",
  "format": "pdf",
  "title": "Mi Documento Académico"
}
```

- `format` puede ser: `"pdf"`, `"word"`, `"ppt"`
- Usa **doble salto de línea** (`\n\n`) para separar secciones/slides
- La respuesta es el archivo para descargar directamente

---

### 🔗 Citaciones — `POST /citations/graph`

Genera un grafo visual de papers que citan al artículo dado por DOI.

**Request:**
```json
{
  "doi": "10.1038/nature12373",
  "max_nodes": 20
}
```

**Response:**
```json
{
  "image_url": "http://localhost:8000/media/graphs/graph_xyz98765.png",
  "total_citations": 15,
  "paper_title": "Título del paper consultado"
}
```

---

## 🗂️ Cómo se Sirven los Archivos (media/)

En `main.py` está esta línea clave:

```python
app.mount("/media", StaticFiles(directory="media"), name="media")
```

Esto hace que FastAPI sirva automáticamente cualquier archivo en la carpeta `media/`
como si fuera un servidor de archivos estático. Por ejemplo:

- Archivo en disco: `media/uml/diagram_abc.png`
- URL pública:      `http://localhost:8000/media/uml/diagram_abc.png`

---

## 🏗️ Arquitectura: ¿Por qué está organizado así?

| Capa | Responsabilidad |
|------|----------------|
| **routers/** | Recibir HTTP, validar con Pydantic, delegar al service |
| **services/** | Lógica de negocio (orquestar el proceso) |
| **models/** | Definir la estructura de los JSON de entrada/salida |
| **utils/** | Funciones reutilizables sin lógica de negocio |

**Ventaja:** Si mañana cambias de PlantUML a otro generador, solo tocas `utils/plantuml.py`.
Si cambias el formato de la respuesta, solo tocas `models/uml_models.py`.

---

## 🧪 Probar con curl

```bash
# UML
curl -X POST http://localhost:8000/uml/generate \
  -H "Content-Type: application/json" \
  -d '{"diagramType":"classDiagram","classes":[{"name":"User","attributes":[{"name":"id","type":"int","visibility":"public"}],"methods":[]}],"relationships":[]}'

# Documento PDF
curl -X POST http://localhost:8000/documents/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola mundo\n\nSegundo párrafo","format":"pdf","title":"Mi Doc"}' \
  --output documento.pdf

# Grafo de citaciones
curl -X POST http://localhost:8000/citations/graph \
  -H "Content-Type: application/json" \
  -d '{"doi":"10.1038/nature12373","max_nodes":15}'
```
