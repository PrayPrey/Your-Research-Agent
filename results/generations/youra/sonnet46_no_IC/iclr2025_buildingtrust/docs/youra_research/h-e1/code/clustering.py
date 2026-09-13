"""
Clustering module for H-E1.
"""

from dataclasses import dataclass
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
import networkx as nx


@dataclass
class ClusterConfig:
    n_clusters: int = 2
    linkage: str = "average"
    metric: str = "precomputed"


def build_distance_matrix(rho_partial: np.ndarray) -> np.ndarray:
    """D = 1 - |rho_partial|, diagonal = 0."""
    D = 1.0 - np.abs(rho_partial)
    np.fill_diagonal(D, 0.0)
    return D


def run_clustering(dist_matrix: np.ndarray, n_clusters: int = 2) -> tuple:
    """Average-linkage clustering with precomputed distance.

    Returns (labels_6, silhouette_score).
    """
    cfg = ClusterConfig()
    clust = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric="precomputed",
        linkage=cfg.linkage,
    )
    labels = clust.fit_predict(dist_matrix)
    sil = silhouette_score(dist_matrix, labels, metric="precomputed")
    return labels, float(sil)


def build_mst(rho_partial: np.ndarray, dim_names: list) -> nx.Graph:
    """Minimum spanning tree on 1 - |rho_partial| distance (H-E2 prerequisite)."""
    G = nx.Graph()
    n = len(dim_names)
    for i in range(n):
        for j in range(i + 1, n):
            weight = 1.0 - abs(rho_partial[i, j])
            G.add_edge(dim_names[i], dim_names[j], weight=weight)
    return nx.minimum_spanning_tree(G, algorithm="kruskal")


def get_dendrogram_linkage(dist_matrix: np.ndarray) -> np.ndarray:
    """scipy linkage for dendrogram plotting."""
    # condensed distance matrix (upper triangle)
    from scipy.spatial.distance import squareform
    condensed = squareform(dist_matrix)
    return linkage(condensed, method="average")
