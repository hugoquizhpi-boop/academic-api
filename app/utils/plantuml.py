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


def json_to_plantuml_class(uml_request) -> str:
    """Genera código PlantUML para diagrama de clases."""
    lines = ["@startuml", ""]

    for cls in uml_request.classes:
        lines.append(f"class {cls.name} {{")
        for attr in cls.attributes:
            symbol = visibility_to_symbol(attr.visibility)
            lines.append(f"  {symbol}{attr.name} : {attr.type}")
        for method in cls.methods:
            symbol = visibility_to_symbol(method.visibility)
            lines.append(f"  {symbol}{method.name} : {method.returnType}")
        lines.append("}")
        lines.append("")

    for rel in uml_request.relationships:
        arrow = relationship_to_plantuml(rel.type)
        if rel.multiplicityFrom or rel.multiplicityTo:
            mult_from = f'"{rel.multiplicityFrom}"' if rel.multiplicityFrom else ""
            mult_to   = f'"{rel.multiplicityTo}"'   if rel.multiplicityTo   else ""
            lines.append(f'{rel.from_} {mult_from} {arrow} {mult_to} {rel.to}')
        else:
            lines.append(f'{rel.from_} {arrow} {rel.to}')

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def json_to_plantuml_usecase(uml_request) -> str:
    """
    Genera código PlantUML para diagrama de casos de uso.
    Las clases con name que empieza en mayúscula y sin atributos/métodos
    se tratan como actores si están en relationships como origen,
    y como casos de uso si están como destino.
    """
    lines = ["@startuml", "left to right direction", ""]

    # Detectar actores y casos de uso desde las relaciones
    actors = set()
    usecases = set()

    for rel in uml_request.relationships:
        actors.add(rel.from_)
        usecases.add(rel.to)

    # Los que aparecen como destino Y origen son actores también
    # Los que solo aparecen como destino son casos de uso
    pure_usecases = usecases - actors

    # Declarar actores
    for cls in uml_request.classes:
        if cls.name in actors:
            lines.append(f'actor "{cls.name}" as {cls.name.replace(" ", "_")}')

    lines.append("")
    lines.append("rectangle Sistema {")

    # Declarar casos de uso
    for cls in uml_request.classes:
        if cls.name in pure_usecases or cls.name in usecases:
            safe_name = cls.name.replace(" ", "_")
            lines.append(f'  usecase "{cls.name}" as {safe_name}')

    lines.append("}")
    lines.append("")

    # Relaciones
    for rel in uml_request.relationships:
        from_safe = rel.from_.replace(" ", "_")
        to_safe = rel.to.replace(" ", "_")
        label = f" : {rel.label}" if rel.label else ""
        lines.append(f"{from_safe} --> {to_safe}{label}")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def json_to_plantuml(uml_request) -> str:
    """
    Convierte un UMLRequest a código PlantUML.
    Detecta el tipo de diagrama y llama a la función correspondiente.

    Tipos soportados:
    - class / classDiagram → diagrama de clases
    - usecase / usecaseDiagram → diagrama de casos de uso
    """
    diagram_type = (uml_request.diagramType or "class").lower().strip()

    if diagram_type in ("usecase", "usecasediagram", "use_case", "use-case"):
        return json_to_plantuml_usecase(uml_request)

    return json_to_plantuml_class(uml_request)


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