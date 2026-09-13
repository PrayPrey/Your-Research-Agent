# Architecture: h-m2 — Epsilon-Threshold Robustness of MLP Activation Sparsity Variation

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Gate:** CV > 0.3 for ≥ 3/4 epsilon values AND max cross-epsilon Kendall's tau ≥ 0.7 for ≥ 1 adjacent pair

Applied: forward-hook-measurement-pattern (accelerate.hooks layerwise casting)
Applied: multi-epsilon-sparsity-sweep (fszatkowski/activation-sparsity-benchmarking)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: patterns found from base code (read via direct file access; Serena project selection unavailable)
**Analyzed Path**: `docs/youra_research/20260508_scope/h-e1/code/`
**Findings**: h-e1 has 5 core modules — `config.py` (ExperimentConfig dataclass, model_name="meta-llama/Meta-Llama-3-8B", epsilons=[0.001, 0.01, 0.05, 0.1]), `data_utils.py` (TokenizedDataset, load_alpaca_dataloader, load_wikitext_dataloader), `measure_sparsity.py` (register_hooks per epsilon, measure_layer_sparsity→np.ndarray(32,), run_all_conditions over 3 datasets × 4 epsilons), `compute_metrics.py` (compute_cv, compute_kendall_tau, compute_all_metrics, check_gate_conditions), `visualize.py` (plot functions + generate_all_figures). h-m2 copies data_utils.py and measure_sparsity.py unchanged, extends config.py with tau thresholds, and adds new compute_metrics.py with cross-epsilon tau logic.

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/20260508_scope/h-e1/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from config import ExperimentConfig` (local copy in h-m2/code/) | `h-e1/code/config.py` → copy to `h-m2/code/config.py` |
| TokenizedDataset | `from data_utils import TokenizedDataset` | `h-e1/code/data_utils.py` → copy to `h-m2/code/data_utils.py` |
| load_alpaca_dataloader | `from data_utils import load_alpaca_dataloader` | `h-e1/code/data_utils.py` |
| load_wikitext_dataloader | `from data_utils import load_wikitext_dataloader` | `h-e1/code/data_utils.py` |
| register_hooks | `from measure_sparsity import register_hooks` | `h-e1/code/measure_sparsity.py` → copy to `h-m2/code/measure_sparsity.py` |
| measure_layer_sparsity | `from measure_sparsity import measure_layer_sparsity` | `h-e1/code/measure_sparsity.py` |

**Note**: All h-e1 modules are copied into h-m2/code/ and imported locally. model_name stays `"meta-llama/Meta-Llama-3-8B"` (same as h-e1, NOT Llama-3.1-8B).

---

## File Organization

```
h-m2/code/
├── config.py              # EXTENDED from h-e1: adds cross_epsilon_tau_threshold, tau_cv_pass_min
├── data_utils.py          # COPIED from h-e1: TokenizedDataset, load_alpaca_dataloader, load_wikitext_dataloader
├── measure_sparsity.py    # COPIED from h-e1: register_hooks, measure_layer_sparsity (unchanged)
├── compute_metrics.py     # NEW: compute_cv_per_epsilon, compute_cross_epsilon_tau, compute_cross_dist_tau, evaluate_gate
├── visualize.py           # NEW: 4 figures for h-m2 (gate_metrics, tau_heatmap, sparsity_overlay, cv_per_epsilon)
├── run_experiment.py      # NEW: main orchestrator for h-m2
├── requirements.txt       # scipy, matplotlib, seaborn (no pingouin needed)
└── tests/
    ├── test_compute_metrics.py
    ├── test_visualize.py
    └── test_run_experiment.py
```

**Output directories** (created at runtime):
```
h-m2/figures/              # 4 PNG outputs
h-m2/experiment_results.json
```

---

## Module Definitions

### Config (`h-m2/code/config.py`)

**Dependencies**: dataclasses, typing
**Status**: EXTENDED from h-e1

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Model settings (unchanged from h-e1)
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings (unchanged from h-e1)
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01
    max_length: int = 512

    # Dataset identifiers (unchanged from h-e1)
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "h-m2/figures"
    results_dir: str = "h-m2"

    # Gate thresholds (h-m2 specific)
    cv_threshold: float = 0.3
    cv_pass_min_count: int = 3          # NEW: ≥ 3 of 4 epsilon values must pass CV gate
    cross_epsilon_tau_threshold: float = 0.7  # NEW: for adjacent pair check
    cross_dist_tau_threshold: float = 0.6     # secondary metric threshold

    def __post_init__(self): ...
```

---

### DataUtils (`h-m2/code/data_utils.py`)

**Dependencies**: torch, datasets, config
**Status**: COPIED from h-e1 (no changes needed)

```python
class TokenizedDataset(Dataset):
    def __init__(self, input_ids_list: List[Tensor]): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader: ...
def load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int = 512) -> DataLoader: ...
```

---

### MeasureSparsity (`h-m2/code/measure_sparsity.py`)

**Dependencies**: torch, numpy, config
**Status**: COPIED from h-e1 (no changes needed)

```python
def register_hooks(
    model,
    epsilon: float,
    layer_counts: List[List[float]],
) -> List: ...

def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray: ...  # shape: (32,)

def run_all_conditions(
    model,
    alpaca_dl: DataLoader,
    wikitext_dl: DataLoader,
    cfg: ExperimentConfig,
) -> dict:
    """Sweep 4 epsilons × 2 datasets → dict[(dataset_name, eps)] = np.ndarray(32,)."""
    ...

def verify_mechanism(layer_sparsity: np.ndarray, cfg: ExperimentConfig) -> tuple[bool, dict]: ...
```

**Note**: `run_all_conditions` in h-m2 uses 2 datasets (Alpaca + WikiText) × 4 epsilons = 8 measurements. Original h-e1 version used 3 dataset configs; h-m2 simplifies to single max_length=512 for both datasets.

---

### ComputeMetrics (`h-m2/code/compute_metrics.py`)

**Dependencies**: numpy, scipy.stats, config
**Status**: NEW (h-m2 primary new module)

```python
from scipy.stats import kendalltau, variation
import numpy as np
from config import ExperimentConfig
from typing import Dict, Tuple, List

ADJACENT_PAIRS = [(0.001, 0.01), (0.01, 0.05), (0.05, 0.1)]

def compute_cv_per_epsilon(
    sparsity_dict: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[float, float]:
    """Compute CV = std/mean for each epsilon sparsity vector. Returns {eps: cv}."""
    ...

def count_cv_pass(
    cv_per_epsilon: Dict[float, float],
    threshold: float = 0.3,
) -> Tuple[int, Dict[float, bool]]:
    """Count how many epsilon values have CV > threshold. Returns (count, {eps: pass})."""
    ...

def compute_cross_epsilon_tau(
    sparsity_dict: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[str, Dict[str, float]]:
    """Compute all C(4,2)=6 pairwise Kendall's tau_b between epsilon sparsity vectors.
    Returns {'{e1}_vs_{e2}': {'tau': float, 'p_value': float}} for all 6 pairs."""
    ...

def compute_cross_dist_tau(
    alpaca_sparsity: Dict[float, np.ndarray],
    wikitext_sparsity: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[float, Dict[str, float]]:
    """For each epsilon, compute Kendall's tau between Alpaca and WikiText sparsity vectors.
    Returns {eps: {'tau': float, 'p_value': float}}."""
    ...

def evaluate_gate(
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Tuple[bool, Dict]:
    """Evaluate combined gate: PASS if count_cv_pass >= 3 AND max adjacent tau >= 0.7.
    Returns (gate_pass: bool, gate_details: dict)."""
    ...

def verify_mechanism_activated(
    sparsity_dict: Dict[float, np.ndarray],
    tau_matrix: Dict[str, Dict[str, float]],
    epsilons: List[float],
) -> Tuple[bool, Dict]:
    """Verify all 32 layers measured, all 4 epsilon vectors computed, all 6 pairs computed."""
    ...
```

---

### Visualize (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, config
**Status**: NEW (h-m2 specific 4 figures)

```python
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import ExperimentConfig

def plot_gate_metrics(
    cv_per_epsilon: dict,
    tau_matrix: dict,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Bar chart: CV values per epsilon and max cross-epsilon tau vs thresholds."""
    ...

def plot_cross_epsilon_tau_heatmap(
    tau_matrix: dict,
    epsilons: list,
    save_path: Path,
) -> None:
    """4x4 symmetric Kendall's tau matrix heatmap (diagonal=1.0, 6 off-diagonal values)."""
    ...

def plot_sparsity_profiles_overlay(
    sparsity_dict: dict,
    epsilons: list,
    save_path: Path,
) -> None:
    """32-layer sparsity profiles for all 4 epsilon values overlaid on single plot."""
    ...

def plot_cv_per_epsilon(
    cv_per_epsilon: dict,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Bar/line chart of CV for each epsilon with 0.3 threshold line."""
    ...

def generate_all_figures(
    sparsity_dict: dict,
    cv_per_epsilon: dict,
    tau_matrix: dict,
    cfg: ExperimentConfig,
) -> None:
    """Save all 4 figures to cfg.figures_dir."""
    ...
```

---

### RunExperiment (`h-m2/code/run_experiment.py`)

**Dependencies**: config, data_utils, measure_sparsity, compute_metrics, visualize, transformers, json
**Status**: NEW

```python
from config import ExperimentConfig
from data_utils import load_alpaca_dataloader, load_wikitext_dataloader
from measure_sparsity import measure_layer_sparsity, verify_mechanism
from compute_metrics import (
    compute_cv_per_epsilon, count_cv_pass,
    compute_cross_epsilon_tau, compute_cross_dist_tau,
    evaluate_gate, verify_mechanism_activated,
)
from visualize import generate_all_figures

def load_model_and_tokenizer(cfg: ExperimentConfig) -> tuple:
    """Load meta-llama/Meta-Llama-3-8B with torch_dtype=float16, device_map=auto."""
    ...

def measure_all_epsilons(
    model,
    alpaca_dl,
    wikitext_dl,
    cfg: ExperimentConfig,
) -> tuple[dict, dict]:
    """Run measure_layer_sparsity for each epsilon on both datasets.
    Returns (alpaca_sparsity_dict, wikitext_sparsity_dict) both keyed by epsilon float."""
    ...

def save_results(
    cv_per_epsilon: dict,
    tau_matrix: dict,
    cross_dist_tau: dict,
    gate_result: bool,
    gate_details: dict,
    cfg: ExperimentConfig,
) -> None:
    """Save experiment_results.json to cfg.results_dir."""
    ...

def main() -> None:
    """Entry point: setup → load → measure → compute → gate → visualize → save."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Verify GPU, set CUDA_VISIBLE_DEVICES, install requirements.txt (scipy, seaborn; no pingouin), copy h-e1 modules | 5 | 1+1+1+2 |
| A-2 | Config Module | Extend h-e1 ExperimentConfig: add cv_pass_min_count=3, cross_epsilon_tau_threshold=0.7, cross_dist_tau_threshold=0.6; update output paths | 6 | 1+1+2+2 |
| A-3 | Dataset Loading | Copy h-e1 data_utils.py; verify load_alpaca_dataloader and load_wikitext_dataloader work with max_length=512, batch_size=8, seed=42 | 7 | 2+2+1+2 |
| A-4 | Multi-Epsilon Sparsity Measurement | Copy h-e1 measure_sparsity.py; implement measure_all_epsilons wrapper that loops over 4 epsilons × 2 datasets = 8 measurement calls | 9 | 2+2+2+3 |
| A-5 | Cross-Epsilon Tau Computation | NEW: implement compute_cross_epsilon_tau (6 pairwise kendalltau_b calls), compute_cv_per_epsilon, count_cv_pass | 12 | 3+2+4+3 |
| A-6 | Cross-Distribution Tau (Secondary) | NEW: implement compute_cross_dist_tau for 4 epsilon × Alpaca vs WikiText comparisons | 8 | 2+2+2+2 |
| A-7 | Gate Evaluation | NEW: implement evaluate_gate combining CV count ≥ 3 AND max adjacent tau ≥ 0.7; verify_mechanism_activated | 10 | 2+2+3+3 |
| A-8 | Visualization | NEW: implement all 4 figures (gate_metrics bar, cross_epsilon tau heatmap via seaborn, sparsity overlay, cv_per_epsilon bar); generate_all_figures | 11 | 3+2+3+3 |
| A-9 | Main Runner Integration | Implement run_experiment.py: load_model_and_tokenizer → measure_all_epsilons → compute metrics → gate → visualize → save; end-to-end orchestration | 10 | 2+3+2+3 |
| A-10 | Results JSON + Gate Reporting | Implement save_results with structured JSON (all CV values, all 6 tau values, gate_result, gate_details); stdout gate summary with gaps to thresholds | 7 | 2+1+2+2 |
| A-11 | Unit Tests | pytest tests for compute_metrics (mock sparsity arrays), visualize (file creation check), run_experiment (smoke test with tiny model or mock); verify_mechanism_activated tests | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-7, A-8, A-9, A-11], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-10]

---

## Data Flow

- `run_experiment.py` → loads model + tokenizer
- `data_utils.py` → alpaca_dl (512 samples), wikitext_dl (512 samples)
- `measure_sparsity.measure_layer_sparsity(model, dl, eps, cfg)` × 8 → `alpaca_sparsity_dict[eps]`, `wikitext_sparsity_dict[eps]`
- `compute_metrics.compute_cv_per_epsilon(alpaca_sparsity_dict)` → `cv_per_epsilon: {eps: float}`
- `compute_metrics.compute_cross_epsilon_tau(alpaca_sparsity_dict)` → `tau_matrix: {pair_str: {tau, p_value}}`
- `compute_metrics.compute_cross_dist_tau(alpaca, wikitext)` → `cross_dist_tau: {eps: {tau, p_value}}`
- `compute_metrics.evaluate_gate(cv_per_epsilon, tau_matrix, cfg)` → `(gate_pass, gate_details)`
- `visualize.generate_all_figures(...)` → 4 PNG files in `h-m2/figures/`
- `run_experiment.save_results(...)` → `h-m2/experiment_results.json`

## Key Constraints

- `measure_layer_sparsity` called once per (dataset, epsilon) pair — no batching across epsilons in single pass (hooks accumulate per-call)
- Model loaded once; all 8 measurements use same loaded model
- `kendalltau(..., variant='b')` for tie-corrected tau_b per FR-4.3
- Adjacent pairs for gate check: (0.001, 0.01), (0.01, 0.05), (0.05, 0.1) — gate passes if any one has tau ≥ 0.7
