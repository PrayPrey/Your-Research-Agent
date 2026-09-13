# Logic: H-E2
## MST Minimum Evaluation Set + Bootstrap Topology Stability

**Hypothesis:** H-E2 (EXISTENCE / PoC — INCREMENTAL on H-E1)
**Date:** 2026-08-04
**Budget:** 2 subtasks (A-2 only)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from actual h-e1 code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:**
- `build_mst(rho_partial: np.ndarray, dim_names: list) -> nx.Graph` — clustering.py:43
- `build_distance_matrix(rho_partial: np.ndarray) -> np.ndarray` — clustering.py:20
- `ols_residualize(scores_df: pd.DataFrame, covariates_df: pd.DataFrame) -> pd.DataFrame` — analysis.py:39
- `partial_spearman_matrix(scores_df, covariates_df, alpha_bonferroni=0.0033) -> tuple` — analysis.py:59

---

## External Dependencies API (Base Hypothesis)

Signatures verified from actual H-E1 code (NOT spec):

```python
# From: h-e1/code/clustering.py (ACTUAL CODE)
def build_mst(
    rho_partial: np.ndarray,   # (N, N) correlation matrix
    dim_names: list            # list of N dimension name strings
) -> nx.Graph:
    """MST on 1 - |rho_partial| distance. Returns nx.Graph with 'weight' edge attr."""
    ...

def build_distance_matrix(
    rho_partial: np.ndarray    # (N, N)
) -> np.ndarray:               # (N, N), diagonal = 0
    """D = 1 - |rho_partial|, diagonal = 0."""
    ...

# From: h-e1/code/analysis.py (ACTUAL CODE)
def ols_residualize(
    scores_df: pd.DataFrame,       # (N, 6) — column names = dim names
    covariates_df: pd.DataFrame    # (N, 2) — log10_params, is_RLHF
) -> pd.DataFrame:                 # (N, 6) OLS residuals
    """OLS-residualize each dimension on covariates."""
    ...

def partial_spearman_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
    alpha_bonferroni: float = 0.0033,
) -> tuple:                        # (rho_matrix [6,6], pval_matrix [6,6], significant_pairs)
    """Returns (rho_partial, pval, significant_pairs)."""
    ...
```

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

**Critical notes:**
- `ols_residualize` takes `pd.DataFrame`, not `np.ndarray` — bootstrap must wrap arrays in DataFrames
- `build_mst` takes raw `rho_partial` (correlation), NOT a distance matrix — it internally computes `1 - |rho|`
- `partial_spearman_matrix` calls `ols_residualize` internally — in bootstrap use only the `rho_matrix` output (index 0)

---

## A-2: Implement mst_analysis.py [Complexity: 12, Budget: 2 subtasks]

Applied: Standard scipy/networkx bootstrap pattern

### API Signatures

```python
# h-e2/code/mst_analysis.py

import sys
import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, FrozenSet

# sys.path.insert(0, "../../h-e1/code") — done at module top or in caller
from clustering import build_mst, build_distance_matrix
from analysis import ols_residualize, partial_spearman_matrix


def compute_mst_metrics(
    mst: nx.Graph,
    dim_names: List[str],         # length 6
) -> Dict:
    """Extract degree, leaf, min_set metrics from MST.
    mst: nx.Graph with 5 edges (n=6 nodes)
    Returns: {"degrees": {dim: int}, "leaves": List[str],
              "min_set": List[str], "min_set_size": int}
    """
    ...


def bootstrap_mst_stability(
    raw_scores: np.ndarray,        # (16, 6)
    covariates: np.ndarray,        # (16, 2)
    dim_names: List[str],          # len=6
    full_mst_edges: FrozenSet,     # frozenset of frozenset({u, v}) pairs
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Tuple[float, Dict[str, float]]:
    """Bootstrap MST topology stability over row subsamples.

    Returns: (topology_stability: float, edge_frequencies: Dict[str, float])
      topology_stability — fraction of n_boot MSTs with identical edge set as full_mst_edges
      edge_frequencies — {"dim_i--dim_j": fraction} for each of 5 full MST edges
    """
    ...


def run_mst_analysis(
    rho_partial: np.ndarray,       # (6, 6) from H-E1 partial_spearman_matrix
    raw_scores: np.ndarray,        # (16, 6)
    covariates: np.ndarray,        # (16, 2)
    dim_names: List[str],          # len=6
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Dict:
    """Full MST analysis: baseline raw Spearman MST + partial MST + bootstrap.

    Returns dict with all gate metrics and intermediate results for serialization.
    Keys: mst_edges, mst_degrees, mst_leaves, mst_min_set, mst_min_set_size,
          bootstrap_topology_stability, bootstrap_edge_frequencies,
          raw_mst_edges, raw_mst_min_set_size,
          gate_primary_passed, gate_secondary_passed, gate_passed
    """
    ...
```

### Tensor Shapes

| Variable | Shape / Type | Note |
|----------|-------------|------|
| raw_scores | (16, 6) ndarray | Input to baseline path and bootstrap |
| covariates | (16, 2) ndarray | log10_params, is_RLHF — wrapped to DataFrame in calls |
| rho_partial | (6, 6) ndarray | From H-E1; diagonal = 1.0 |
| full_mst_edges | FrozenSet | frozenset of frozenset({u, v}) pairs |
| topology_stability | float | scalar in [0, 1] |
| edge_frequencies | Dict[str, float] | 5 keys, "dim_i--dim_j" format |
| degrees | Dict[str, int] | 6 keys — one per dim |
| min_set_size | int | scalar, gate threshold <= 4 |

### Pseudo-code: compute_mst_metrics

```
degrees  = dict(mst.degree())                         # {dim: int}
leaves   = [n for n, d in degrees.items() if d == 1]
min_set  = [n for n, d in degrees.items() if d > 1]
return {"degrees": degrees, "leaves": leaves,
        "min_set": min_set, "min_set_size": len(min_set)}
```

### Pseudo-code: bootstrap_mst_stability

```
rng = np.random.default_rng(seed)
scores_df   = pd.DataFrame(raw_scores, columns=dim_names)
cov_df      = pd.DataFrame(covariates, columns=["log10_params", "is_RLHF"])

# helper: canonical edge key for string dict
def edge_key(u, v): return "--".join(sorted([u, v]))
def edges_to_frozenset(g): return frozenset(frozenset({u, v}) for u, v in g.edges())

edge_counts = {edge_key(*sorted(e)): 0 for e in full_mst_edges}
match_count = 0

for _ in range(n_boot):
    idx        = rng.choice(16, size=subsample, replace=False)
    sub_scores = scores_df.iloc[idx].reset_index(drop=True)   # (14, 6) DataFrame
    sub_cov    = cov_df.iloc[idx].reset_index(drop=True)      # (14, 2) DataFrame

    rho_boot, _, _ = partial_spearman_matrix(sub_scores, sub_cov)  # (6, 6)
    mst_boot       = build_mst(rho_boot, dim_names)
    boot_edges     = edges_to_frozenset(mst_boot)

    if boot_edges == full_mst_edges:
        match_count += 1
    for e in boot_edges:
        key = edge_key(*sorted(e))
        if key in edge_counts:
            edge_counts[key] += 1

topology_stability = match_count / n_boot
edge_frequencies   = {k: v / n_boot for k, v in edge_counts.items()}
return topology_stability, edge_frequencies
```

### Pseudo-code: run_mst_analysis

```
from scipy.stats import spearmanr

scores_df = pd.DataFrame(raw_scores, columns=dim_names)

# Baseline: raw Spearman MST
rho_raw, _ = spearmanr(raw_scores)      # (6, 6) when input is 2D
raw_mst    = build_mst(rho_raw, dim_names)
raw_metrics = compute_mst_metrics(raw_mst, dim_names)

# Primary: partial Spearman MST from H-E1 rho_partial
partial_mst = build_mst(rho_partial, dim_names)
assert len(partial_mst.edges()) == 5    # n-1 edges for 6 nodes
partial_metrics = compute_mst_metrics(partial_mst, dim_names)

full_mst_edges = frozenset(frozenset({u, v}) for u, v in partial_mst.edges())

# Bootstrap
stability, edge_freqs = bootstrap_mst_stability(
    raw_scores, covariates, dim_names, full_mst_edges, n_boot, subsample, seed
)

# Gate
gate_primary   = partial_metrics["min_set_size"] <= 4
gate_secondary = stability >= 0.90
return {
    "mst_edges":  [(u, v, d["weight"]) for u, v, d in partial_mst.edges(data=True)],
    "mst_degrees": partial_metrics["degrees"],
    "mst_leaves":  partial_metrics["leaves"],
    "mst_min_set": partial_metrics["min_set"],
    "mst_min_set_size": partial_metrics["min_set_size"],
    "bootstrap_topology_stability": stability,
    "bootstrap_edge_frequencies":   edge_freqs,
    "raw_mst_edges": [(u, v) for u, v in raw_mst.edges()],
    "raw_mst_min_set_size": raw_metrics["min_set_size"],
    "gate_primary_passed":   gate_primary,
    "gate_secondary_passed": gate_secondary,
    "gate_passed": gate_primary and gate_secondary,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | compute_mst_metrics | Degree dict, leaf list, min_set list, min_set_size from nx.Graph |
| L-2-2 | bootstrap_mst_stability | 1000x subsample → OLS residualize → partial Spearman → MST → edge set compare + per-edge freq |
