"""
Utilidad para trabajar con PlantUML.
"""

import zlib
import base64
import httpx
import string

PLANTUML_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
BASE64_ALPHABET   = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"

def encode_plantuml(plantuml_code: str) -> str:
    compressed = zlib.compress(plantuml_code.encode("utf-8"))[2:-4]
    b64 = base64.b64encode(compressed).decode("ascii")
    result = ""
    for char in b64:
        if char in BASE64_ALPHABET:
            idx = BASE64_ALPHABET.index(char)
            result += PLANTUML_ALPHABET[idx]
        else:
            result += char
    return result


def visibility_to_symbol(visibility: str) -> str:
    mapping = {"public": "+", "private": "-", "protected": "#", "package": "~"}
    return mapping.get(visibility.lower(), "+")


def relationship_to_plantuml(rel_type: str) -> str:
    mapping = {
        "association": "--", "inheritance": "<|--", "composition": "*--",
        "aggregation": "o--", "dependency": "..>", "realization": "<|..",
    }
    return mapping.get(rel_type.lower(), "--")


def safe_alias(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")


def json_to_plantuml_class(uml_request) -> str:
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
    lines = [
        "@startuml",
        "left to right direction",
        "",
        "skinparam actorStyle awesome",
        "skinparam ArrowColor #2E75B6",
        "skinparam ArrowThickness 1.5",
        "skinparam usecase {",
        "  BackgroundColor #E8F4F8",
        "  BorderColor #2E75B6",
        "  FontSize 11",
        "}",
        "skinparam actor {",
        "  BackgroundColor #D4E8F0",
        "  BorderColor #1B4F72",
        "  FontSize 11",
        "}",
        "",
    ]

    actors = set()
    usecases = set()
    for rel in uml_request.relationships:
        actors.add(rel.from_)
        usecases.add(rel.to)
    pure_usecases = usecases - actors

    for cls in uml_request.classes:
        if cls.name in actors:
            lines.append(f'actor "{cls.name}" as {safe_alias(cls.name)}')

    lines.append("")
    lines.append("rectangle Sistema {")
    for cls in uml_request.classes:
        if cls.name in pure_usecases or cls.name in usecases:
            lines.append(f'  usecase "{cls.name}" as {safe_alias(cls.name)}')
    lines.append("}")
    lines.append("")

    for rel in uml_request.relationships:
        label = f" : {rel.label}" if rel.label else ""
        lines.append(f"{safe_alias(rel.from_)} --> {safe_alias(rel.to)}{label}")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def json_to_plantuml(uml_request) -> str:
    diagram_type = (uml_request.diagramType or "class").lower().strip()
    if diagram_type in ("usecase", "usecasediagram", "use_case", "use-case"):
        return json_to_plantuml_usecase(uml_request)
    return json_to_plantuml_class(uml_request)


async def generate_plantuml_image(plantuml_code: str, output_path: str) -> bool:
    encoded = encode_plantuml(plantuml_code)
    url = f"https://www.plantuml.com/plantuml/png/{encoded}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    return False