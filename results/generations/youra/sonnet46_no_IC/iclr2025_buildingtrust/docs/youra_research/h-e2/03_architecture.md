# Architecture: H-E2
## MST Minimum Evaluation Set + Bootstrap Topology Stability

**Hypothesis:** H-E2 (EXISTENCE / PoC — INCREMENTAL on H-E1)
**Date:** 2026-08-04
**Applied:** standard experiment-module pattern (1 new module, max reuse from base)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** `build_mst()` already implemented in `clustering.py` (lines 42-50); `ols_residualize()` in `analysis.py` (lines 38-46). Both are directly reusable with no modification. H-E1 main.py pattern: `check_gate` + `serialize_results` + `run_experiment` — same pattern used in H-E2 main.py.

---

## File Organization

**h-e2/code/** (new files only):
- `mst_analysis.py` — MST bootstrap logic (NEW)
- `main.py` — orchestration entry point (NEW, mirrors h-e1 pattern)
- `figures/` — output figures directory

**h-e1/code/** (reused as-is, not copied):
- `data_loader.py` — load_trustllm_scores, add_annotations, validate
- `analysis.py` — ols_residualize, partial_spearman_matrix
- `clustering.py` — build_mst, build_distance_matrix

---

## Module Structure

### MSTAnalysis (`h-e2/code/mst_analysis.py`)

**Dependencies:** `sys.path` insert for `h-e1/code/` → imports `clustering.build_mst`, `analysis.ols_residualize`, `analysis.partial_spearman_matrix`

```python
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, FrozenSet

def compute_mst_metrics(
    mst: nx.Graph,
    dim_names: List[str]
) -> Dict:
    """Returns degrees, leaves, min_set, min_set_size from MST graph."""
    ...

def bootstrap_mst_stability(
    raw_scores: np.ndarray,       # (16, 6)
    covariates: np.ndarray,       # (16, 2)
    dim_names: List[str],
    full_mst_edges: FrozenSet,
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42
) -> Tuple[float, Dict[str, float]]:
    """
    Returns:
        topology_stability: float — fraction of boot MSTs matching full edge set
        edge_frequencies: Dict[str, float] — per-edge bootstrap presence fraction
    """
    ...

def run_mst_analysis(
    rho_partial: np.ndarray,      # (6, 6) from H-E1
    raw_scores: np.ndarray,       # (16, 6)
    covariates: np.ndarray,       # (16, 2)
    dim_names: List[str]
) -> Dict:
    """
    Full analysis: baseline MST (raw Spearman) + partial Spearman MST + bootstrap.
    Returns all gate metrics and intermediate results.
    """
    ...
```

### Main (`h-e2/code/main.py`)

**Dependencies:** `mst_analysis`, `data_loader` (h-e1), `visualization`

```python
def check_gate(results: Dict) -> bool:
    """Gate: mst_min_set_size <= 4 AND bootstrap_topology_stability >= 0.90"""
    ...

def serialize_results(results: Dict, out_path: str) -> None:
    """Write experiment_results_phase3.json to h-e2/"""
    ...

def run_experiment(h_e1_results_path: str, out_dir: str) -> Dict:
    """
    Load h-e1 outputs → run MST analysis → visualize → serialize → check gate.
    Prints summary to console and writes experiment.log.
    """
    ...

if __name__ == "__main__":
    # argparse: --h_e1_results, --out_dir, --n_boot, --seed
    ...
```

---

## External Dependencies (Base Hypothesis)

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_trustllm_scores | `sys.path.insert(0, "../h-e1/code"); from data_loader import load_trustllm_scores` | `h-e1/code/data_loader.py` |
| add_annotations | `from data_loader import add_annotations` | `h-e1/code/data_loader.py` |
| ols_residualize | `from analysis import ols_residualize` | `h-e1/code/analysis.py` |
| partial_spearman_matrix | `from analysis import partial_spearman_matrix` | `h-e1/code/analysis.py` |
| build_mst | `from clustering import build_mst` | `h-e1/code/clustering.py` |
| build_distance_matrix | `from clustering import build_distance_matrix` | `h-e1/code/clustering.py` |

**Note:** H-E2 code runs from `h-e2/code/` with `sys.path.insert(0, "../../h-e1/code")` to access H-E1 modules. No copying needed.

---

## Data Flow

- Input: `h-e1/experiment_results_phase3.json` → `rho_partial (6,6)`, `raw_scores (16,6)`, `model_metadata`
- Baseline path: `raw_scores` → `scipy.stats.spearmanr` → `build_mst` → `compute_mst_metrics` → `raw_mst_min_set_size`
- Primary path: `rho_partial` (from H-E1) → `build_mst` → `compute_mst_metrics` → `mst_min_set_size`
- Bootstrap path: 1000× subsample `raw_scores[14/16]` → `ols_residualize` → `partial_spearman_matrix` → `build_mst` → edge set comparison
- Output: `h-e2/experiment_results_phase3.json`, `h-e2/figures/*.png`, `h-e2/experiment.log`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project scaffold | Create h-e2/code/ dir, figures/ dir, sys.path wiring, smoke-test H-E1 imports | 5 | 1+1+1+2 |
| A-2 | Implement mst_analysis.py | `compute_mst_metrics`, `bootstrap_mst_stability`, `run_mst_analysis` | 12 | 3+2+4+3 |
| A-3 | Implement main.py | Load H-E1 JSON, orchestrate analysis, `check_gate`, `serialize_results`, log | 8 | 2+2+2+2 |
| A-4 | Visualization | 4 figures: gate bar chart, MST graph, bootstrap heatmap, distance heatmap + MST comparison | 10 | 2+2+3+3 |
| A-5 | End-to-end run + validation | Run full experiment, assert MST has 5 edges, verify outputs match gate thresholds | 7 | 1+2+2+2 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [A-2, A-4] | Low(4-8): [A-1, A-3, A-5]

**Total subtask estimate:** 5+12+8+10+7 = 42 points across 5 epics (LIGHT tier, within 4-8 task range)

---

## Environment

- Conda env: `youra-h-e1` (Python 3.10) — no new packages needed
- Packages: numpy, scipy, scikit-learn, networkx, matplotlib, seaborn (all pre-installed)
- Seed: `np.random.seed(42)` in bootstrap
- Runtime: < 60s CPU (1000 bootstrap × 6×6 OLS residualization)
