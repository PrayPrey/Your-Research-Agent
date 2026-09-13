"""
H-E2: MST Minimum Evaluation Set + Bootstrap Topology Stability.
"""

import os
import sys

import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import spearmanr
from typing import Dict, List, Tuple, FrozenSet

# Import H-E1 modules via relative sys.path
_H_E1_CODE = os.path.join(os.path.dirname(__file__), "../../h-e1/code")
sys.path.insert(0, os.path.abspath(_H_E1_CODE))

from clustering import build_mst, build_distance_matrix
from analysis import ols_residualize, partial_spearman_matrix


def compute_mst_metrics(mst: nx.Graph, dim_names: List[str]) -> Dict:
    degrees = dict(mst.degree())
    leaves = [n for n, d in degrees.items() if d == 1]
    min_set = [n for n, d in degrees.items() if d > 1]
    return {
        "degrees": degrees,
        "leaves": leaves,
        "min_set": min_set,
        "min_set_size": len(min_set),
    }


def bootstrap_mst_stability(
    raw_scores: np.ndarray,
    covariates: np.ndarray,
    dim_names: List[str],
    full_mst_edges: FrozenSet,
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Tuple[float, Dict[str, float]]:
    rng = np.random.default_rng(seed)
    scores_df = pd.DataFrame(raw_scores, columns=dim_names)
    cov_df = pd.DataFrame(covariates, columns=["log10_params", "is_RLHF"])

    def edge_key(u, v):
        return "--".join(sorted([u, v]))

    def edges_to_frozenset(g):
        return frozenset(frozenset({u, v}) for u, v in g.edges())

    edge_counts = {edge_key(*sorted(e)): 0 for e in full_mst_edges}
    match_count = 0

    for _ in range(n_boot):
        idx = rng.choice(len(raw_scores), size=subsample, replace=False)
        sub_scores = scores_df.iloc[idx].reset_index(drop=True)
        sub_cov = cov_df.iloc[idx].reset_index(drop=True)

        rho_boot, _, _ = partial_spearman_matrix(sub_scores, sub_cov)
        mst_boot = build_mst(rho_boot, dim_names)
        boot_edges = edges_to_frozenset(mst_boot)

        if boot_edges == full_mst_edges:
            match_count += 1
        for e in boot_edges:
            key = edge_key(*sorted(e))
            if key in edge_counts:
                edge_counts[key] += 1

    topology_stability = match_count / n_boot
    edge_frequencies = {k: v / n_boot for k, v in edge_counts.items()}
    return topology_stability, edge_frequencies


def run_mst_analysis(
    rho_partial: np.ndarray,
    raw_scores: np.ndarray,
    covariates: np.ndarray,
    dim_names: List[str],
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Dict:
    # Baseline: raw Spearman MST
    rho_raw_result = spearmanr(raw_scores)
    rho_raw = rho_raw_result.statistic if hasattr(rho_raw_result, 'statistic') else rho_raw_result.correlation
    raw_mst = build_mst(rho_raw, dim_names)
    raw_metrics = compute_mst_metrics(raw_mst, dim_names)

    # Primary: partial Spearman MST from H-E1 rho_partial
    partial_mst = build_mst(rho_partial, dim_names)
    assert len(partial_mst.edges()) == 5, f"MST should have 5 edges, got {len(partial_mst.edges())}"
    partial_metrics = compute_mst_metrics(partial_mst, dim_names)

    full_mst_edges = frozenset(frozenset({u, v}) for u, v in partial_mst.edges())

    # Bootstrap
    stability, edge_freqs = bootstrap_mst_stability(
        raw_scores, covariates, dim_names, full_mst_edges, n_boot, subsample, seed
    )

    gate_primary = partial_metrics["min_set_size"] <= 4
    gate_secondary = stability >= 0.90

    return {
        "mst_edges": [(u, v, d["weight"]) for u, v, d in partial_mst.edges(data=True)],
        "mst_degrees": partial_metrics["degrees"],
        "mst_leaves": partial_metrics["leaves"],
        "mst_min_set": partial_metrics["min_set"],
        "mst_min_set_size": partial_metrics["min_set_size"],
        "bootstrap_topology_stability": stability,
        "bootstrap_edge_frequencies": edge_freqs,
        "raw_mst_edges": [(u, v) for u, v in raw_mst.edges()],
        "raw_mst_min_set_size": raw_metrics["min_set_size"],
        "gate_primary_passed": gate_primary,
        "gate_secondary_passed": gate_secondary,
        "gate_passed": gate_primary and gate_secondary,
    }
