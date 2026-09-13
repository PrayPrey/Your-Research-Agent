# H-M4 Architecture: Layer-wise Grassmann Distance Analysis

**Applied**: analysis-pipeline pattern (layer-wise decomposition of aggregate distance matrix)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (base_hypothesis)
**Status**: Patterns found from H-M3 base code
**Analyzed Path**: `docs/youra_research/20260413_wsl/h-m3/code/`
**Findings**: H-M3 uses flat module pattern (config.py, grassmann_loader.py, correlation.py, visualize.py, run_experiment.py). Adapter metadata confirmed at `h-e1/results/adapter_metadata.json` with adapter paths `h-e1/adapters/{task}_seed{n}` (integer seeds 0-4). H-M4 extends H-M3 by decomposing aggregate distance into per-layer-type distances.

---

## File Organization

```
h-m4/
├── code/
│   ├── config.py
│   ├── adapter_loader.py
│   ├── layer_distances.py
│   ├── statistics.py
│   ├── visualize.py
│   ├── run_experiment.py
│   └── tests/
│       └── test_core.py
├── results/
│   ├── layer_distances.npz
│   ├── cohens_d_results.json
│   └── analysis_summary.json
└── figures/
    ├── cohens_d_by_layer_type.png
    ├── layer_type_ranking.png
    ├── attention_vs_mlp.png
    └── best_layer_heatmap.png
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
import os, sys
from pathlib import Path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_DIR: str          # abs path to h-e1/
H_E1_RESULTS_DIR: str  # h-e1/results/
H_E1_ADAPTER_DIR: str  # h-e1/adapters/
H_E1_CODE_DIR: str     # h-e1/code/ (added to sys.path)

HYPOTHESIS_FOLDER: str
RESULTS_DIR: str
FIGURES_DIR: str

TASKS: list[str]       # [gsm8k, arc, logiqa, strategyqa, mnli, qqp, sst2, mrpc]
SEEDS: list[int]       # [0, 1, 2, 3, 4]
N_ADAPTERS: int        # 40

TASK_CATEGORIES: dict[str, str]  # task -> "reasoning" | "nlu"

ATTENTION_LAYER_TYPES: list[str]  # [q_proj, k_proj, v_proj, o_proj]
MLP_LAYER_TYPES: list[str]        # [up_proj, down_proj, gate_proj]
ALL_LAYER_TYPES: list[str]        # ATTENTION + MLP (7 total)
N_TRANSFORMER_LAYERS: int         # 22

LORA_CONFIG: dict  # r=32, alpha=64, target_modules=ALL_LAYER_TYPES

ANALYSIS_CONFIG: dict  # cohens_d_threshold=0.8, n_bootstrap=2000, random_seed=42, ci_level=0.95

VIZ_CONFIG: dict   # figsize, colors, dpi=150, format=png
```

---

### AdapterLoader (`code/adapter_loader.py`)

**Dependencies**: config, safetensors, numpy

```python
from pathlib import Path
from typing import NamedTuple
import numpy as np

class AdapterRecord(NamedTuple):
    task: str
    seed: int
    category: str
    path: str

def load_adapter_metadata(h_e1_results_dir: str) -> list[AdapterRecord]: ...
    # Reads h-e1/results/adapter_metadata.json
    # Returns 40 AdapterRecord entries sorted by (task, seed)

def load_b_matrices(
    record: AdapterRecord,
    layer_type: str,
) -> list[np.ndarray]: ...
    # Loads safetensors from record.path
    # Filters keys matching f"*.{layer_type}.lora_B.weight"
    # Returns list of 22 matrices (one per transformer layer)

def load_all_b_matrices(
    records: list[AdapterRecord],
    layer_type: str,
) -> np.ndarray: ...
    # Returns array shape (40, 22, hidden_dim, r) for given layer_type
    # Calls load_b_matrices for each record

def validate_adapter_count(records: list[AdapterRecord], expected: int = 40) -> None: ...
```

---

### LayerDistances (`code/layer_distances.py`)

**Dependencies**: config, adapter_loader, numpy, torch

```python
import numpy as np
import torch
from typing import Optional

def grassmann_distance(A: np.ndarray, B: np.ndarray) -> float: ...
    # QR decompose A, B -> Q_A, Q_B
    # SVD of Q_A.T @ Q_B -> singular values S
    # clamp S to [-1, 1] for numerical stability
    # return ||arccos(S)||_2

def compute_layer_type_distance_matrix(
    all_b_matrices: np.ndarray,
    layer_type: str,
) -> np.ndarray: ...
    # all_b_matrices: (40, 22, dim, r)
    # For each pair (i, j): average grassmann_distance across 22 layers
    # Returns symmetric (40, 40) distance matrix

def compute_all_layer_type_distances(
    records: list,
    layer_types: list[str],
) -> dict[str, np.ndarray]: ...
    # Returns {layer_type: (40, 40) distance matrix} for all 7 types
    # Calls compute_layer_type_distance_matrix per type
    # Logs progress per layer type

def save_layer_distances(
    distances: dict[str, np.ndarray],
    output_path: str,
) -> None: ...
    # Saves as .npz with layer_type keys

def load_layer_distances(path: str) -> dict[str, np.ndarray]: ...
```

---

### Statistics (`code/statistics.py`)

**Dependencies**: config, numpy, scipy, pingouin

```python
import numpy as np
from typing import TypedDict

class CohensDResult(TypedDict):
    layer_type: str
    cohens_d: float
    ci_low: float
    ci_high: float
    p_value: float
    n_within: int
    n_between: int

def split_within_between(
    distance_matrix: np.ndarray,
    records: list,
) -> tuple[np.ndarray, np.ndarray]: ...
    # records provide task/category per adapter
    # within: pairs where both adapters share same category
    # between: pairs where adapters differ in category
    # excludes diagonal (self-distances)

def compute_cohens_d_with_ci(
    within: np.ndarray,
    between: np.ndarray,
    n_bootstrap: int = 2000,
    random_seed: int = 42,
) -> tuple[float, float, float]: ...
    # Pooled std Cohen's d: (mean_between - mean_within) / pooled_std
    # Bootstrap CI via pingouin.compute_bootci
    # Returns (d, ci_low, ci_high)

def analyze_all_layer_types(
    distances: dict[str, np.ndarray],
    records: list,
) -> list[CohensDResult]: ...
    # Calls split_within_between + compute_cohens_d_with_ci for each layer type
    # Returns list sorted by cohens_d descending

def compute_group_statistics(
    results: list[CohensDResult],
    attention_types: list[str],
    mlp_types: list[str],
) -> dict: ...
    # Mean/std Cohen's d for attention group vs MLP group
    # Mann-Whitney U test for group difference
    # Returns {attention_mean, mlp_mean, p_value, group_difference}

def evaluate_gate(results: list[CohensDResult], threshold: float = 0.8) -> dict: ...
    # Returns {passed: bool, best_layer: str, max_d: float, layers_above_threshold: list}
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config, statistics, numpy, matplotlib, seaborn

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

def plot_cohens_d_by_layer_type(
    results: list,
    output_path: str,
    threshold: float = 0.8,
) -> None: ...
    # Bar chart: Cohen's d per layer type with CI error bars
    # Horizontal threshold line at d=0.8
    # Color-coded by attention (blue) vs MLP (orange)

def plot_layer_type_ranking(
    results: list,
    output_path: str,
) -> None: ...
    # Horizontal bar chart sorted by Cohen's d descending
    # Includes CI whiskers

def plot_attention_vs_mlp(
    results: list,
    group_stats: dict,
    output_path: str,
) -> None: ...
    # Box/violin plot: attention group vs MLP group Cohen's d distribution
    # Annotate with group means and p-value

def plot_best_layer_heatmap(
    distance_matrix: np.ndarray,
    records: list,
    best_layer_type: str,
    output_path: str,
) -> None: ...
    # 8x8 task-level mean distance heatmap for highest-d layer type
    # Aggregate 40x40 -> 8x8 by averaging seeds per task pair

def generate_all_figures(
    results: list,
    distances: dict[str, np.ndarray],
    records: list,
    group_stats: dict,
    figures_dir: str,
) -> None: ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
import json
from pathlib import Path

def run(force_recompute: bool = False) -> dict: ...
    # 1. Load adapter metadata (adapter_loader)
    # 2. Compute layer-type distance matrices (layer_distances)
    # 3. Run statistical analysis (statistics)
    # 4. Evaluate gate (statistics)
    # 5. Generate figures (visualize)
    # 6. Save results to JSON
    # 7. Return analysis_summary dict

def save_results(
    cohens_d_results: list,
    group_stats: dict,
    gate_result: dict,
    output_dir: str,
) -> None: ...

if __name__ == "__main__":
    run()
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| AdapterMetadata | `h-e1/results/adapter_metadata.json` | `h-e1/results/adapter_metadata.json` |
| Adapter safetensors | `h-e1/adapters/{task}_seed{n}/adapter_model.safetensors` | `h-e1/adapters/` |
| H-E1 pairwise distances | `h-e1/results/pairwise_distances.npy` | `h-e1/results/` (optional cross-check) |

**Verified from**: `h-e1/results/adapter_metadata.json` (actual paths use integer seeds 0-4, format `{task}_seed{n}`)

**Note**: PRD specifies `seed_42` format but actual metadata uses integer seeds (0-4). Code must use integer seed format.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config.py, path setup mirroring H-M3 | 5 | 1+1+1+2 |
| A-2 | Adapter Loading | adapter_loader.py: load metadata, load B matrices per layer type | 10 | 2+2+3+3 |
| A-3 | Grassmann Distance | layer_distances.py: grassmann_distance, compute per layer type | 14 | 3+2+5+4 |
| A-4 | Statistical Analysis | statistics.py: Cohen's d, bootstrap CI, group comparison, gate eval | 15 | 3+3+5+4 |
| A-5 | Visualization | visualize.py: 4 required figures | 10 | 2+2+3+3 |
| A-6 | Integration & Runner | run_experiment.py: orchestrate pipeline, save results | 8 | 2+3+1+2 |
| A-7 | Tests | test_core.py: unit tests for grassmann, cohen's d, split logic | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-2, A-5, A-7], Low(4-8): [A-1, A-6]
