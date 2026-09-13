# Architecture: H-M3
## RLHF Causal Chain Produces 2-Cluster Trustworthiness Correlation Structure

**Date:** 2026-08-04
**Hypothesis Type:** MECHANISM (Step 3 of 3)
**Applied:** No relevant KB pattern (Archon KB is diffusion-focused; all clustering patterns sourced from experiment brief)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code (h-m2/code/)
**Analyzed Path:** docs/youra_research/h-m2/code/
**Findings:** H-M2 uses 4-file flat layout (config.py, analysis.py, visualization.py, main.py). Config uses `_HERE`/`_RESEARCH` path anchoring relative to `__file__`. Import paths use direct local imports (no package). H-M3 mirrors this exactly.

---

## File Structure

```
h-m3/
├── code/
│   ├── config.py          # paths + constants
│   ├── analysis.py        # clustering + metrics
│   ├── visualization.py   # all figure generation
│   └── main.py            # entry point + results persistence
├── figures/               # output figures (auto-created)
└── experiment_results_h_m3.json  # output results
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| HE1_JSON path | `from config import HE1_JSON` | `h-m3/code/config.py` (mirrors h-m2 pattern) |
| rho_partial | loaded via `json.load(open(HE1_JSON))["rho_partial"]` | `h-e1/experiment_results_phase3.json` |

**Verified from:** `docs/youra_research/h-m2/code/config.py` (actual implementation)
Path pattern: `_RESEARCH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`

---

## Modules

### Config (`code/config.py`)

**Dependencies:** stdlib only

```python
import os

_HERE: str       # os.path.dirname(os.path.abspath(__file__))
_HM3: str        # dirname(_HERE) -> h-m3/
_RESEARCH: str   # dirname(dirname(_HM3)) -> youra_research/

HE1_JSON: str    # _RESEARCH/h-e1/experiment_results_phase3.json
OUTPUT_DIR: str  # _HM3
FIGURES_DIR: str # _HM3/figures
RESULTS_JSON: str  # _HM3/experiment_results_h_m3.json

DIMENSIONS: list[str]  # ["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]
SAFETY_IDX: int        # 1
ROBUSTNESS_IDX: int    # 3
ETHICS_IDX: int        # 5

PREDICTED_RLHF_SENSITIVE: set[str]    # {"safety", "machine_ethics"}
PREDICTED_RLHF_INSENSITIVE: set[str]  # {"robustness", "privacy"}

PRIMARY_SILHOUETTE_THRESHOLD: float   # 0.3
SECONDARY_ALIGNMENT_THRESHOLD: int    # 4
N_CLUSTERS: int  # 2
RANDOM_SEED: int  # 1
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** config, numpy, scipy, sklearn

```python
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.manifold import MDS

def load_rho_partial(he1_json_path: str) -> tuple[np.ndarray, list[str]]:
    """Load 6x6 rho_partial matrix from h-e1 results.
    Returns: (rho_partial (6,6), dims list)
    """
    ...

def validate_rho_matrix(rho: np.ndarray) -> None:
    """Assert shape==(6,6), symmetric, diag==1, values in [-1,1]. Raises ValueError."""
    ...

def make_distance_matrix(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """d = clip(1-rho, 0, 2), diag=0. Returns (dist_matrix (6,6), condensed (15,))."""
    ...

def run_ward_clustering(condensed: np.ndarray, dist_matrix: np.ndarray, n_clusters: int = 2) -> dict:
    """scipy Ward linkage. Returns dict with keys: Z, labels, silhouette."""
    ...

def compute_membership_alignment(labels: np.ndarray, dims: list[str]) -> int:
    """Best-of-two label assignment alignment against PREDICTED_RLHF_SENSITIVE/INSENSITIVE.
    Returns int in [0, 4]."""
    ...

def run_alternative_linkages(dist_matrix: np.ndarray, dims: list[str]) -> dict:
    """Run average + complete linkage; return dict of silhouette scores."""
    ...

def run_k3_check(condensed: np.ndarray, dist_matrix: np.ndarray) -> float:
    """Ward at k=3; return silhouette_k3."""
    ...

def run_alt_distance(rho: np.ndarray, dims: list[str]) -> dict:
    """d=sqrt(1-rho^2); re-run Ward; return silhouette_alt."""
    ...

def run_mds_projection(dist_matrix: np.ndarray, seed: int = 1) -> np.ndarray:
    """2D MDS on distance matrix. Returns coords (6, 2)."""
    ...

def run_analysis(he1_json_path: str) -> dict:
    """Full pipeline. Returns all results dict for serialization."""
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** config, analysis (results dict), matplotlib, seaborn, scipy.cluster.hierarchy.dendrogram

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.cluster.hierarchy import dendrogram

def plot_gate_metrics(results: dict, figures_dir: str) -> str:
    """Bar chart: silhouette_ward vs 0.3 threshold + alignment vs 4/6. Returns path."""
    ...

def plot_dendrogram(Z: np.ndarray, dims: list[str], labels: np.ndarray, figures_dir: str) -> str:
    """Ward dendrogram with leaf color by predicted cluster membership. Returns path."""
    ...

def plot_rho_heatmap(rho: np.ndarray, dims: list[str], labels: np.ndarray, figures_dir: str) -> str:
    """6x6 heatmap reordered by cluster; diverging colormap; cluster boundaries. Returns path."""
    ...

def plot_silhouette_comparison(results: dict, figures_dir: str) -> str:
    """Bar chart: ward vs average vs complete silhouette for k=2. Returns path."""
    ...

def plot_mds_projection(coords: np.ndarray, dims: list[str], labels: np.ndarray, figures_dir: str) -> str:
    """2D MDS scatter colored by cluster; annotated. Returns path."""
    ...

def generate_all_figures(results: dict, figures_dir: str) -> list[str]:
    """Call all plot_* functions. Returns list of figure paths."""
    ...
```

---

### Main (`code/main.py`)

**Dependencies:** config, analysis, visualization, json, os

```python
import json, os

def serialize_results(results: dict) -> dict:
    """Convert numpy types to Python native for JSON serialization."""
    ...

def check_gate(results: dict) -> str:
    """Evaluate PASS/PARTIAL_PASS/FAIL. Never raises. Returns gate string."""
    ...

def run_experiment() -> None:
    """Entry point: load -> analyze -> visualize -> save results JSON -> print gate."""
    ...

if __name__ == "__main__":
    run_experiment()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Paths | config.py with path anchoring, constants, predicted cluster sets | 5 | 1+1+1+2 |
| A-2 | Data Loading + Validation | load_rho_partial + validate_rho_matrix (FR-1.1–1.6) | 6 | 1+2+1+2 |
| A-3 | Distance Matrix Construction | make_distance_matrix (d=clip(1-rho,0,2), squareform) | 5 | 1+2+1+1 |
| A-4 | Ward Clustering (Primary Gate) | run_ward_clustering via scipy linkage+fcluster+silhouette_score(precomputed) | 9 | 2+2+3+2 |
| A-5 | Membership Alignment (Secondary Gate) | compute_membership_alignment with best-of-two label assignment | 7 | 1+2+2+2 |
| A-6 | Robustness Checks | run_alternative_linkages + run_k3_check + run_alt_distance (FR-5.1–5.4) | 10 | 2+2+3+3 |
| A-7 | Visualization (5 figures) | plot_gate_metrics + dendrogram + heatmap + silhouette_comparison + mds_projection | 13 | 3+2+4+4 |
| A-8 | Results Persistence + Gate Logic | serialize_results + check_gate + JSON write (FR-8.1–8.3) | 7 | 1+2+2+2 |
| A-9 | Main Entry Point Integration | run_experiment wiring all modules; SHOULD_WORK compliance (never raise on gate fail) | 8 | 1+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-8, A-9]

---

## Critical Implementation Notes (for Phase 4 Coder)

- **FORBIDDEN**: `AgglomerativeClustering(linkage='ward', metric='precomputed')` — sklearn #27655, still open
- **REQUIRED**: `scipy.cluster.hierarchy.linkage(squareform(dist_matrix), method='ward')` then `fcluster(Z, t=2, criterion='maxclust') - 1`
- **Silhouette**: `silhouette_score(dist_matrix, labels, metric='precomputed')` — supports precomputed
- **Gate behavior**: SHOULD_WORK — always write results JSON, never sys.exit on failure
- **Path anchor**: mirror h-m2 pattern — `_RESEARCH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
- **HE1_JSON**: `os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")`
- **MDS seed**: pass `random_state=RANDOM_SEED` to sklearn MDS for reproducibility
