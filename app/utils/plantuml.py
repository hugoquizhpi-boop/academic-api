"""
Utilidad para trabajar con PlantUML.

¿Cómo funciona?
1. Convertimos el JSON a código PlantUML (texto plano)
2. Enviamos ese código al servidor público de PlantUML (plantuml.com)
3. Descargamos la imagen PNG resultante
4. La guardamos en /media/uml/

No necesitamos instalar Java ni PlantUML localmente.
"""

import zlib
import base64
import httpx
import string

# Alfabeto especial que usa PlantUML para codificar URLs
PLANTUML_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
BASE64_ALPHABET   = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"

def encode_plantuml(plantuml_code: str) -> str:
    """
    Convierte código PlantUML a formato URL-safe.
    PlantUML usa su propio encoding basado en deflate + base64 modificado.
    """
    # 1. Comprimir con zlib (deflate)
    compressed = zlib.compress(plantuml_code.encode("utf-8"))[2:-4]

    # 2. Codificar en base64
    b64 = base64.b64encode(compressed).decode("ascii")

    # 3. Traducir al alfabeto de PlantUML
    result = ""
    for char in b64:
        if char in BASE64_ALPHABET:
            idx = BASE64_ALPHABET.index(char)
            result += PLANTUML_ALPHABET[idx]
        else:
            result += char

    return result


def visibility_to_symbol(visibility: str) -> str:
    """Convierte visibilidad en texto a símbolo PlantUML."""
    mapping = {
        "public":    "+",
        "private":   "-",
        "protected": "#",
        "package":   "~",
    }
    return mapping.get(visibility.lower(), "+")


def relationship_to_plantuml(rel_type: str) -> str:
    """Convierte tipo de relación a sintaxis PlantUML."""
    mapping = {
        "association":  "--",
        "inheritance":  "<|--",
        "composition":  "*--",
        "aggregation":  "o--",
        "dependency":   "..>",
        "realization":  "<|..",
    }
    return mapping.get(rel_type.lower(), "--")


def json_to_plantuml(uml_request) -> str:
    """
    Convierte un UMLRequest a código PlantUML.

    Ejemplo de salida:
        @startuml
        class Usuario {
          +id : int
          +nombre : string
          +login() : void
        }
        Usuario "1" -- "*" Pedido
        @enduml
    """
    lines = ["@startuml", ""]

    # ── Generar cada clase ────────────────────────────────────────────────────
    for cls in uml_request.classes:
        lines.append(f"class {cls.name} {{")

        # Atributos
        for attr in cls.attributes:
            symbol = visibility_to_symbol(attr.visibility)
            lines.append(f"  {symbol}{attr.name} : {attr.type}")

        # Métodos
        for method in cls.methods:
            symbol = visibility_to_symbol(method.visibility)
            lines.append(f"  {symbol}{method.name} : {method.returnType}")

        lines.append("}")
        lines.append("")

    # ── Generar relaciones ────────────────────────────────────────────────────
    for rel in uml_request.relationships:
        arrow = relationship_to_plantuml(rel.type)

        # Con multiplicidad: Usuario "1" -- "*" Pedido
        if rel.multiplicityFrom or rel.multiplicityTo:
            mult_from = f'"{rel.multiplicityFrom}"' if rel.multiplicityFrom else ""
            mult_to   = f'"{rel.multiplicityTo}"'   if rel.multiplicityTo   else ""
            lines.append(f'{rel.from_} {mult_from} {arrow} {mult_to} {rel.to}')
        else:
            lines.append(f'{rel.from_} {arrow} {rel.to}')

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


async def generate_plantuml_image(plantuml_code: str, output_path: str) -> bool:
    """
    Envía el código PlantUML al servidor público y descarga la imagen PNG.

    Args:
        plantuml_code: El código @startuml ... @enduml
        output_path: Ruta donde guardar el PNG

    Returns:
        True si fue exitoso, False si hubo error
    """
    encoded = encode_plantuml(plantuml_code)
    url = f"https://www.plantuml.com/plantuml/png/{encoded}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True

    return False
