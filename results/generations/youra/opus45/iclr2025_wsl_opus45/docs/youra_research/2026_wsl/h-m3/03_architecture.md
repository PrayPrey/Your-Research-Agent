# Architecture: H-M3 - FLAN Taxonomy Correlation with Grassmann Distances

**Applied**: correlation-analysis-reuse pattern
**Applied**: spearman-bootstrap-ci pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (read directly via filesystem - Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/20260413_wsl/h-e1/code/`
**Findings**: H-E1 has 6 modules (config.py, data.py, train.py, analyze.py, visualize.py, run_experiment.py). Key reusable: `extract_b_matrices`, `compute_pairwise_matrix`, `grassmann_distance`, `split_within_between` in analyze.py; `TASK_CATEGORIES` dict and path constants in config.py; `generate_all_figures` pattern in visualize.py.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| extract_b_matrices | `from h_e1_analyze import extract_b_matrices` (copy-or-symlink) | `h-e1/code/analyze.py` |
| compute_pairwise_matrix | `from h_e1_analyze import compute_pairwise_matrix` | `h-e1/code/analyze.py` |
| grassmann_distance | `from h_e1_analyze import grassmann_distance` | `h-e1/code/analyze.py` |
| split_within_between | `from h_e1_analyze import split_within_between` | `h-e1/code/analyze.py` |
| TASK_CATEGORIES | `from config import TASK_CATEGORIES` | `h-e1/code/config.py` |
| _bootstrap_ci | `from h_e1_analyze import _bootstrap_ci` | `h-e1/code/analyze.py` |

**Verified from**: `docs/youra_research/20260413_wsl/h-e1/code/` (actual implementation)

**Note on import strategy**: H-M3 code lives in `h-m3/code/`. H-E1 functions are imported by adding `h-e1/code/` to `sys.path` in config.py, or by copying needed functions. The architecture below uses a `h_e1_bridge.py` shim to centralize this.

---

## File Organization

- `h-m3/code/`
  - `config.py` - paths, thresholds, FLAN categories
  - `h_e1_bridge.py` - imports/re-exports H-E1 functions
  - `grassmann_loader.py` - load or recompute distance matrix
  - `taxonomy.py` - FLAN taxonomy distance matrix
  - `correlation.py` - Spearman correlation + bootstrap CI + P3 control
  - `visualize.py` - 4 figures extending H-E1 patterns
  - `run_experiment.py` - orchestration entry point

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none (stdlib only)

```python
import os
import sys

# H-E1 bridge: add h-e1/code to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_CODE_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1/code"))
H_E1_HYPOTHESIS_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1"))
if H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, H_E1_CODE_DIR)

HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")

# FLAN taxonomy - ground truth categories
FLAN_CATEGORIES: dict[str, str] = {
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

ANALYSIS_CONFIG: dict = {
    "spearman_rho_threshold": 0.3,
    "p_threshold": 0.05,
    "n_bootstrap": 1000,
    "random_seed": 42,
    "p3_ratio_threshold": 0.5,
}

SEEDS: list[int] = [42, 43, 44, 45, 46]
TASKS: list[str] = list(FLAN_CATEGORIES.keys())
N_ADAPTERS: int = 40  # 8 tasks x 5 seeds
```

---

### H-E1 Bridge (`code/h_e1_bridge.py`)

**Dependencies**: Config (sys.path setup), h-e1/code/analyze.py

```python
# Re-exports H-E1 functions after sys.path is configured by config.py
import config  # noqa: F401 - triggers sys.path insertion

from analyze import (
    extract_b_matrices,
    compute_pairwise_matrix,
    grassmann_distance,
    compute_orthonormal_basis,
    split_within_between,
    _bootstrap_ci,
)

__all__ = [
    "extract_b_matrices",
    "compute_pairwise_matrix",
    "grassmann_distance",
    "compute_orthonormal_basis",
    "split_within_between",
    "_bootstrap_ci",
]
```

---

### GrassmannLoader (`code/grassmann_loader.py`)

**Dependencies**: Config, H-E1 Bridge

```python
import numpy as np
from typing import Optional

def load_or_compute_distances(
    h_e1_hypothesis_dir: str,
    force_recompute: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """
    Load precomputed distances from H-E1 results, or recompute from adapters.

    Returns:
        distance_matrix: (40, 40) symmetric float array
        adapter_meta: list of {adapter_path, task, seed, category}
    """
    ...

def validate_distance_matrix(
    distance_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    """
    Assert shape (N,N), symmetric, zero diagonal, finite values.
    Raises ValueError on failure.
    """
    ...

def load_adapter_metadata(
    h_e1_results_dir: str,
) -> list[dict]:
    """Load adapter_metadata.json from H-E1 results."""
    ...
```

---

### TaxonomyMatrix (`code/taxonomy.py`)

**Dependencies**: Config

```python
import numpy as np
from typing import Optional

FLAN_CATEGORIES: dict[str, str]  # imported from config

def build_taxonomy_distance_matrix(
    task_labels: list[str],
    flan_categories: dict[str, str],
    mode: str = "binary",
) -> np.ndarray:
    """
    Build (N, N) taxonomy distance matrix.

    Args:
        task_labels: ordered list of task names for each adapter
        flan_categories: mapping task -> category string
        mode: "binary" (0=same, 1=different) or "hierarchical"

    Returns:
        taxonomy_matrix: (N, N) float array
    """
    ...

def extract_task_labels_from_meta(
    adapter_meta: list[dict],
) -> list[str]:
    """Extract ordered task name list from adapter metadata dicts."""
    ...

def save_taxonomy_matrix(
    taxonomy_matrix: np.ndarray,
    results_dir: str,
    filename: str = "taxonomy_distances.npy",
) -> None: ...
```

---

### CorrelationAnalyzer (`code/correlation.py`)

**Dependencies**: Config, H-E1 Bridge (_bootstrap_ci)

```python
import numpy as np
from scipy.stats import spearmanr
from typing import NamedTuple

class CorrelationResult(NamedTuple):
    spearman_rho: float
    p_value: float
    ci_low: float
    ci_high: float
    n_pairs: int
    gate_passed: bool

class P3ControlResult(NamedTuple):
    within_task_mean: float
    within_cluster_mean: float
    ratio: float
    control_passed: bool

def compute_spearman_correlation(
    grassmann_matrix: np.ndarray,
    taxonomy_matrix: np.ndarray,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> CorrelationResult:
    """
    Flatten upper triangles of both matrices, compute Spearman rho + p-value
    + bootstrap 95% CI.

    Returns CorrelationResult with gate_passed = (rho > 0.3 and p < 0.05).
    """
    ...

def compute_p3_control(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    ratio_threshold: float = 0.5,
) -> P3ControlResult:
    """
    Extract within-task distances (same task, different seeds) and
    within-cluster distances (same category, different tasks).

    Returns P3ControlResult with control_passed = (within_task_mean < threshold * within_cluster_mean).
    """
    ...

def _flatten_upper_triangle(matrix: np.ndarray) -> np.ndarray:
    """Return 1D array of upper triangle values (k=1)."""
    ...

def save_correlation_results(
    corr: CorrelationResult,
    p3: P3ControlResult,
    results_dir: str,
    filename: str = "correlation_results.json",
) -> None: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config, CorrelationAnalyzer result types

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from correlation import CorrelationResult, P3ControlResult

def plot_gate_metrics_bar(
    corr: CorrelationResult,
    out_dir: str,
) -> None:
    """Bar chart: Spearman rho vs threshold 0.3 with p-value + CI annotation."""
    ...

def plot_scatter_regression(
    grassmann_flat: np.ndarray,
    taxonomy_flat: np.ndarray,
    corr: CorrelationResult,
    out_dir: str,
) -> None:
    """Scatter plot of Grassmann vs taxonomy distances with regression line."""
    ...

def plot_correlation_heatmap(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    out_dir: str,
) -> None:
    """Task-level mean distance heatmap (8x8), sorted by FLAN category."""
    ...

def plot_p3_control_distributions(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    p3: P3ControlResult,
    out_dir: str,
) -> None:
    """KDE/box: within-task vs within-cluster distance distributions."""
    ...

def generate_all_figures(
    hypothesis_folder: str,
    grassmann_matrix: np.ndarray,
    taxonomy_matrix: np.ndarray,
    adapter_meta: list[dict],
    corr: CorrelationResult,
    p3: P3ControlResult,
) -> None:
    """Generate and save all 4 figures to {hypothesis_folder}/figures/."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, GrassmannLoader, TaxonomyMatrix, CorrelationAnalyzer, Visualizer

```python
import argparse

def parse_args() -> argparse.Namespace: ...

def run(force_recompute: bool = False) -> dict:
    """
    Orchestration:
    1. Load/compute Grassmann distance matrix (GrassmannLoader)
    2. Build FLAN taxonomy distance matrix (TaxonomyMatrix)
    3. Compute Spearman correlation + P3 control (CorrelationAnalyzer)
    4. Save results JSON
    5. Generate figures (Visualizer)
    6. Print gate pass/fail summary

    Returns: combined results dict for downstream consumption
    """
    ...

def print_gate_summary(corr: "CorrelationResult", p3: "P3ControlResult") -> None:
    """Print structured pass/fail summary to stdout."""
    ...

if __name__ == "__main__":
    args = parse_args()
    results = run(force_recompute=args.force_recompute)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project scaffold | Create h-m3/code/ structure, config.py with paths and FLAN_CATEGORIES, h_e1_bridge.py | 6 | 1+1+2+2 |
| A-2 | GrassmannLoader | Load pairwise_distances.npy from H-E1 results + validate (shape, symmetry, zero diag); fallback recompute via H-E1 bridge | 9 | 2+3+2+2 |
| A-3 | Adapter metadata parsing | Load adapter_metadata.json from H-E1, parse task labels and seeds, validate 40 adapters × 8 tasks × 5 seeds | 7 | 2+2+2+1 |
| A-4 | TaxonomyMatrix | Build (40,40) binary FLAN taxonomy distance matrix from task labels; verify structure | 8 | 2+1+3+2 |
| A-5 | Spearman correlation | Flatten upper triangles, scipy.stats.spearmanr, bootstrap 95% CI (n=1000), gate evaluation (rho>0.3, p<0.05) | 12 | 3+2+4+3 |
| A-6 | P3 control analysis | Extract within-task pairs (same task, diff seed) vs within-cluster pairs (same category, diff task); validate ratio < 0.5 | 11 | 3+3+3+2 |
| A-7 | Results serialization | Save correlation_results.json with all metrics; validate JSON schema matches PRD spec | 6 | 1+2+1+2 |
| A-8 | Gate metrics bar chart | Bar chart: Spearman rho vs 0.3 threshold with CI error bars and significance annotation | 8 | 2+2+2+2 |
| A-9 | Scatter + regression plot | Grassmann distance vs taxonomy distance scatter with OLS regression line and rho annotation | 9 | 2+2+3+2 |
| A-10 | Correlation heatmap | 8x8 task-level mean distance heatmap sorted by FLAN category with boundary annotations | 9 | 2+2+3+2 |
| A-11 | P3 control plot | KDE/boxplot of within-task vs within-cluster distributions with control threshold line | 8 | 2+2+2+2 |
| A-12 | Orchestration + validation | run_experiment.py wiring all modules, CLI args, gate summary print, end-to-end smoke test | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-6, A-9, A-10, A-12], Low(4-8): [A-1, A-2, A-3, A-4, A-7, A-8, A-11]

---

## Data Flow

- H-E1 `results/pairwise_distances.npy` + `results/adapter_metadata.json`
  - GrassmannLoader validates and returns (40,40) matrix + meta list
- adapter_meta (task labels) -> TaxonomyMatrix -> (40,40) binary matrix
- Both matrices -> CorrelationAnalyzer -> CorrelationResult + P3ControlResult
- All above -> Visualizer -> 4 figures in `h-m3/figures/`
- CorrelationResult + P3ControlResult -> `h-m3/results/correlation_results.json`

## Gate Evaluation

| Metric | Threshold | Source |
|--------|-----------|--------|
| Spearman rho | > 0.3 | CorrelationResult.spearman_rho |
| p-value | < 0.05 | CorrelationResult.p_value |
| P3 control ratio | within_task < 0.5 * within_cluster | P3ControlResult.control_passed |
