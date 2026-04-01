"""
Utilidad para generar grafos de citaciones.
"""

import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict


def build_citation_graph(
    root_title: str,
    citations: List[Dict],
    output_path: str,
    max_nodes: int = 20
) -> int:
    citations = citations[:max_nodes]

    G = nx.DiGraph()

    def short_title(title: str, max_len: int = 45) -> str:
        return title[:max_len] + "..." if len(title) > max_len else title

    root_label = short_title(root_title)
    G.add_node(root_label, node_type="root")

    for paper in citations:
        label = short_title(paper.get("title", "Sin título"))
        G.add_node(label, node_type="citation")
        G.add_edge(root_label, label)

    # Layout con más separación entre nodos
    if len(G.nodes) > 1:
        pos = nx.spring_layout(G, k=4.0, seed=42)
    else:
        pos = {root_label: (0, 0)}

    node_colors = []
    node_sizes  = []
    for node in G.nodes:
        if G.nodes[node].get("node_type") == "root":
            node_colors.append("#2563EB")
            node_sizes.append(800)       # Más pequeño para que el texto quepa
        else:
            node_colors.append("#10B981")
            node_sizes.append(600)

    fig, ax = plt.subplots(figsize=(18, 13))  # Canvas más grande
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
        arrowsize=15,
        width=1.5,
        alpha=0.7,
        ax=ax
    )

    # Etiquetas FUERA de los nodos (sobre ellos)
    label_pos = {node: (x, y + 0.08) for node, (x, y) in pos.items()}
    nx.draw_networkx_labels(
        G, label_pos,
        font_size=7,
        font_color="#1E293B",   # Texto oscuro para leer sobre fondo claro
        font_weight="bold",
        ax=ax,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor="#CBD5E1",
            alpha=0.85
        )
    )

    legend_patches = [
        mpatches.Patch(color="#2563EB", label="Paper consultado"),
        mpatches.Patch(color="#10B981", label="Paper citado"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=10)

    ax.set_title(
        f"Grafo de Citaciones\n{short_title(root_title, 80)}",
        fontsize=12,
        fontweight="bold",
        pad=20
    )
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return len(citations)