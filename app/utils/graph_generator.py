"""
Utilidad para generar grafos de citaciones.

Usa networkx para la estructura del grafo y matplotlib para renderizarlo.
"""

import networkx as nx
import matplotlib
matplotlib.use("Agg")  # Backend sin pantalla (necesario en servidor)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict


def build_citation_graph(
    root_title: str,
    citations: List[Dict],
    output_path: str,
    max_nodes: int = 20
) -> int:
    """
    Construye y guarda una imagen del grafo de citaciones.

    Args:
        root_title: Título del paper raíz (el que buscamos por DOI)
        citations: Lista de dicts con {"title": str, "doi": str}
        output_path: Ruta donde guardar la imagen PNG
        max_nodes: Máximo de nodos a mostrar

    Returns:
        Número de citas mostradas en el grafo
    """
    # Limitar cantidad de nodos
    citations = citations[:max_nodes]

    # ── Crear el grafo dirigido ───────────────────────────────────────────────
    G = nx.DiGraph()

    # Acortar títulos largos para que quepan en el nodo
    def short_title(title: str, max_len: int = 40) -> str:
        return title[:max_len] + "..." if len(title) > max_len else title

    root_label = short_title(root_title)
    G.add_node(root_label, node_type="root")

    for paper in citations:
        label = short_title(paper.get("title", "Sin título"))
        G.add_node(label, node_type="citation")
        G.add_edge(root_label, label)

    # ── Layout del grafo ──────────────────────────────────────────────────────
    # spring_layout da buena distribución para grafos de citaciones
    if len(G.nodes) > 1:
        pos = nx.spring_layout(G, k=2.5, seed=42)
    else:
        pos = {root_label: (0, 0)}

    # ── Colores por tipo de nodo ──────────────────────────────────────────────
    node_colors = []
    node_sizes  = []
    for node in G.nodes:
        if G.nodes[node].get("node_type") == "root":
            node_colors.append("#2563EB")  # Azul para el nodo raíz
            node_sizes.append(3000)
        else:
            node_colors.append("#10B981")  # Verde para citas
            node_sizes.append(1500)

    # ── Dibujar ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        ax=ax
    )

    nx.draw_networkx_edges(
        G, pos,
        edge_color="#94A3B8",
        arrows=True,
        arrowsize=20,
        width=1.5,
        alpha=0.7,
        ax=ax
    )

    nx.draw_networkx_labels(
        G, pos,
        font_size=7,
        font_color="white",
        font_weight="bold",
        ax=ax
    )

    # ── Leyenda ───────────────────────────────────────────────────────────────
    legend_patches = [
        mpatches.Patch(color="#2563EB", label="Paper consultado"),
        mpatches.Patch(color="#10B981", label="Paper citado"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=10)

    ax.set_title(
        f"Grafo de Citaciones\n{short_title(root_title, 70)}",
        fontsize=12,
        fontweight="bold",
        pad=20
    )
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return len(citations)
