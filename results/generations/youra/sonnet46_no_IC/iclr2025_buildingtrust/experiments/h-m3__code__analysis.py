"""Analysis module for H-M3: Ward clustering on rho_partial from H-E1."""
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.manifold import MDS

from config import (
    DIMENSIONS, N_CLUSTERS, RANDOM_SEED,
    PREDICTED_RLHF_SENSITIVE, PREDICTED_RLHF_INSENSITIVE,
    PRIMARY_SILHOUETTE_THRESHOLD, SECONDARY_ALIGNMENT_THRESHOLD,
)


def load_rho_partial(he1_json_path: str) -> tuple:
    with open(he1_json_path) as f:
        data = json.load(f)
    rho = np.array(data["rho_partial"])  # (6,6)
    return rho, DIMENSIONS


def validate_rho_matrix(rho: np.ndarray) -> None:
    if rho.shape != (6, 6):
        raise ValueError(f"rho_partial must be (6,6), got {rho.shape}")
    if not np.allclose(rho, rho.T, atol=1e-6):
        raise ValueError("rho_partial must be symmetric")
    if not np.allclose(np.diag(rho), 1.0, atol=1e-6):
        raise ValueError("rho_partial diagonal must be 1.0")
    if not (np.all(rho >= -1.0) and np.all(rho <= 1.0)):
        raise ValueError("rho_partial values must be in [-1, 1]")


def make_distance_matrix(rho: np.ndarray) -> tuple:
    dist = np.clip(1.0 - rho, 0.0, 2.0)
    np.fill_diagonal(dist, 0.0)
    condensed = squareform(dist)  # (15,)
    return dist, condensed


def run_ward_clustering(condensed: np.ndarray, dist_matrix: np.ndarray, n_clusters: int = N_CLUSTERS) -> dict:
    Z = linkage(condensed, method='ward')
    labels = fcluster(Z, t=n_clusters, criterion='maxclust') - 1  # 0-indexed
    sil = silhouette_score(dist_matrix, labels, metric='precomputed')
    gate_pass = sil > PRIMARY_SILHOUETTE_THRESHOLD
    cluster_membership = {DIMENSIONS[i]: int(labels[i]) for i in range(len(DIMENSIONS))}
    if gate_pass:
        print(f"✓ PRIMARY GATE PASS: silhouette_ward={sil:.4f} > {PRIMARY_SILHOUETTE_THRESHOLD}")
    else:
        print(f"EXPLORE: silhouette_ward={sil:.4f} — below {PRIMARY_SILHOUETTE_THRESHOLD} threshold")
    return {
        "Z": Z,
        "labels": labels,
        "silhouette_ward": sil,
        "primary_gate_pass": gate_pass,
        "cluster_membership": cluster_membership,
    }


def compute_membership_alignment(labels: np.ndarray, dims: list) -> int:
    cluster_membership = {dims[i]: int(labels[i]) for i in range(len(dims))}
    best = 0
    for sensitive_label in [0, 1]:
        count = sum(
            1 for dim, lbl in cluster_membership.items()
            if (dim in PREDICTED_RLHF_SENSITIVE and lbl == sensitive_label)
            or (dim in PREDICTED_RLHF_INSENSITIVE and lbl != sensitive_label)
        )
        best = max(best, count)
    if best >= SECONDARY_ALIGNMENT_THRESHOLD:
        print(f"✓ SECONDARY GATE PASS: membership_alignment={best}/4")
    else:
        print(f"EXPLORE: membership_alignment={best}/4 — below {SECONDARY_ALIGNMENT_THRESHOLD} threshold")
    return best


def run_alternative_linkages(dist_matrix: np.ndarray, dims: list) -> dict:
    results = {}
    for method in ['average', 'complete']:
        model = AgglomerativeClustering(n_clusters=2, metric='precomputed', linkage=method)
        labels = model.fit_predict(dist_matrix)
        sil = silhouette_score(dist_matrix, labels, metric='precomputed')
        results[f"silhouette_{method}"] = float(sil)
        results[f"labels_{method}"] = labels
    return results


def run_k3_check(condensed: np.ndarray, dist_matrix: np.ndarray) -> float:
    Z = linkage(condensed, method='ward')
    labels_k3 = fcluster(Z, t=3, criterion='maxclust') - 1
    return float(silhouette_score(dist_matrix, labels_k3, metric='precomputed'))


def run_alt_distance(rho: np.ndarray, dims: list) -> dict:
    dist_alt = np.sqrt(np.clip(1 - rho**2, 0, 1))
    np.fill_diagonal(dist_alt, 0)
    condensed_alt = squareform(dist_alt)
    Z_alt = linkage(condensed_alt, method='ward')
    labels_alt = fcluster(Z_alt, t=2, criterion='maxclust') - 1
    sil_alt = float(silhouette_score(dist_alt, labels_alt, metric='precomputed'))
    return {"silhouette_alt_distance": sil_alt, "labels_alt": labels_alt}


def run_mds_projection(dist_matrix: np.ndarray, seed: int = RANDOM_SEED) -> np.ndarray:
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=seed, normalized_stress='auto')
    return mds.fit_transform(dist_matrix)


def run_analysis(he1_json_path: str) -> dict:
    rho, dims = load_rho_partial(he1_json_path)
    validate_rho_matrix(rho)
    dist_matrix, condensed = make_distance_matrix(rho)

    ward = run_ward_clustering(condensed, dist_matrix, n_clusters=N_CLUSTERS)
    alignment = compute_membership_alignment(ward["labels"], dims)

    alt_linkages = run_alternative_linkages(dist_matrix, dims)
    sil_k3 = run_k3_check(condensed, dist_matrix)
    alt_dist = run_alt_distance(rho, dims)
    coords = run_mds_projection(dist_matrix, seed=RANDOM_SEED)

    return {
        "rho": rho,
        "dims": dims,
        "dist_matrix": dist_matrix,
        "condensed": condensed,
        "Z": ward["Z"],
        "labels": ward["labels"],
        "silhouette_ward": ward["silhouette_ward"],
        "primary_gate_pass": ward["primary_gate_pass"],
        "cluster_membership": ward["cluster_membership"],
        "membership_alignment": alignment,
        "secondary_gate_pass": alignment >= SECONDARY_ALIGNMENT_THRESHOLD,
        "silhouette_average": alt_linkages["silhouette_average"],
        "silhouette_complete": alt_linkages["silhouette_complete"],
        "silhouette_k3": sil_k3,
        "silhouette_alt_distance": alt_dist["silhouette_alt_distance"],
        "labels_alt": alt_dist["labels_alt"],
        "mds_coords": coords,
    }
