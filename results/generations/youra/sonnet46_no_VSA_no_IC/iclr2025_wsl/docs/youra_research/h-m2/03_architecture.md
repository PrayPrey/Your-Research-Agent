---
hypothesis_id: h-m2
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-21"
---

# Architecture: H-M2 — Sample Efficiency via Permutation Equivariance

Applied: continuation-first pattern (load H-E1 results → skip training if present)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 + H-M1)
**Status**: patterns found from base code (Glob + Read; Serena project selector unavailable)
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`

**Findings**:
- H-E1 has `encoders.py` (FlatMLP, FlatMLPPermAug, NFNEncoder, GNNNFNEncoder, build_encoder), `data.py` (ZooDataset, load_zoo, subsample, FlatCollator, GNNCollator, state_dict_to_graph), `train.py` (train_one, get_predictions), `config.py`, `evaluate.py`, `visualize.py`, `run_experiment.py`
- H-M1 has `permute.py` (permute_weights, permute_all_hidden_layers, get_perm), `verify.py`, `encoder_loader.py`, `data_loader.py`
- H-E1 config shows only `cifar10` zoo was actually run (MNIST path absent); `ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]` — NFN dropped due to CNN zoo incompatibility
- H-E1 results path: `docs/youra_research/h-e1/results/` (check for `learning_curve_results.json`)
- DWSNets NOT in H-E1 actual encoder list — treat as optional with explicit compatibility check

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| FlatMLP | `sys.path.insert(0, h_e1_code); from encoders import FlatMLP` | `h-e1/code/encoders.py` |
| FlatMLPPermAug | `from encoders import FlatMLPPermAug` | `h-e1/code/encoders.py` |
| GNNNFNEncoder | `from encoders import GNNNFNEncoder` | `h-e1/code/encoders.py` |
| build_encoder | `from encoders import build_encoder` | `h-e1/code/encoders.py` |
| ZooDataset | `from data import ZooDataset, load_zoo, subsample` | `h-e1/code/data.py` |
| make_flat_loader | `from data import make_flat_loader, make_gnn_loader` | `h-e1/code/data.py` |
| state_dict_to_graph | `from data import state_dict_to_graph` | `h-e1/code/data.py` |
| train_one | `from train import train_one, get_predictions` | `h-e1/code/train.py` |
| permute_weights | `sys.path.insert(0, h_m1_code); from permute import permute_weights` | `h-m1/code/permute.py` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m1/code/` actual files

**Critical note**: H-E1 config uses hardcoded absolute paths. H-M2 config must override `ZOO_PATHS` and `MZDATASET_CODE_PATH` for local environment.

---

## File Organization

```
docs/youra_research/h-m2/
  code/
    config.py          # paths, hyperparams, experiment grid
    results_loader.py  # load H-E1 results OR run training fallback
    analysis.py        # efficiency ratio + bootstrap CI computation
    visualize.py       # learning curve plots + bar charts
    run_experiment.py  # entry point: orchestrate full pipeline
  results/
    learning_curve_results.json
  figures/
    learning_curves_mnist.png
    learning_curves_cifar10.png
    efficiency_ratio_bar.png
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: os, sys

```python
import os, sys

H_E1_CODE = os.path.join(os.path.dirname(__file__), "../../h-e1/code")
H_M1_CODE = os.path.join(os.path.dirname(__file__), "../../h-m1/code")
H_E1_RESULTS_JSON = os.path.join(os.path.dirname(__file__), "../../h-e1/results/learning_curve_results.json")

MZDATASET_CODE_PATH: str  # override locally
ZOO_PATHS: dict            # {"mnist": "...", "cifar10": "..."}

TRAINING_SIZES = [100, 250, 500, 1000, "full"]
SEEDS = [0, 1, 2, 3, 4]
EPOCHS = 100
LR = 1e-3
WEIGHT_DECAY = 1e-4
BATCH_SIZE = 32
BATCH_SIZE_SMALL = 16  # for N <= 250
BUDGET_TIERS = {"small": 50_000, "medium": 200_000, "large": 500_000}
PRIMARY_TIER = "medium"
ZOO_NAMES = ["mnist", "cifar10"]
ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]  # dwsnets added if compatible
PEAK_FRACTION = 0.90
EFFICIENCY_GATE = 2.0

FIGURES_DIR: str
RESULTS_DIR: str
DEVICE: str
```

---

### ResultsLoader (`code/results_loader.py`)

**Dependencies**: config, H-E1 code (encoders, data, train), H-M1 code (permute)

```python
import json
from typing import Optional

def load_h_e1_results(path: str) -> Optional[dict]:
    """Load {encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi, seed_r2s}}}} or None."""
    ...

def run_training_fallback(
    encoder_names: list,
    zoo_names: list,
    training_sizes: list,
    seeds: list,
    device: str,
) -> dict:
    """
    Re-run H-E1 training protocol for all cells missing from H-E1 results.
    Returns same schema as load_h_e1_results.
    Calls build_encoder, load_zoo, subsample, make_flat_loader/make_gnn_loader,
    train_one, get_predictions from H-E1 code.
    """
    ...

def check_dwsnets_compatibility(zoo_name: str) -> bool:
    """
    Return True if CNN-s zoo has >2 FC layers (DWSNets requirement).
    If False, log limitation and exclude DWSNets from encoder_names.
    """
    ...

def get_results(device: str = "cpu") -> dict:
    """
    Primary entry point.
    1. Try load_h_e1_results(H_E1_RESULTS_JSON)
    2. If None or incomplete: run_training_fallback for missing cells
    3. Return merged results dict
    """
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: numpy, scipy, config

```python
import numpy as np
from typing import Union

def compute_efficiency_ratio(
    plain_curve: dict,   # {size -> float}
    equiv_curve: dict,   # {size -> float}
    peak_fraction: float = 0.90,
) -> float:
    """N_plain(90% peak) / N_equiv(90% peak). Returns inf if equiv never reaches threshold."""
    ...

def bootstrap_ci(
    seed_r2s: list,
    n_boot: int = 1000,
    ci: float = 0.95,
) -> tuple:
    """Returns (mean, lo, hi) via percentile bootstrap over seed_r2s."""
    ...

def compute_all_efficiency_ratios(results: dict) -> dict:
    """
    results: {encoder: {zoo: {size: {mean_r2, ...}}}}
    Returns {encoder: {zoo: efficiency_ratio}} for equivariant encoders vs flat_mlp.
    """
    ...

def verify_mechanism_activated(encoder, test_batch, zoo_arch: str, encoder_name: str) -> dict:
    """
    Sanity check: equivariance holds (max_diff < 1e-4) on one batch.
    Returns {"equivariance_holds": bool, "max_diff": float}.
    Only called for gnn_nfn (dwsnets if present).
    """
    ...

def check_gate(efficiency_ratios: dict) -> tuple:
    """
    Returns (gate_passed: bool, best_ratio: float, best_encoder: str, best_zoo: str).
    Gate: ratio >= 2.0 for >=1 equivariant encoder on BOTH mnist and cifar10.
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, config

```python
def plot_learning_curves(
    results: dict,           # {encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi}}}}
    zoo_name: str,
    out_path: str,
) -> None:
    """Line plot: R² vs training size for all encoders. 95% CI bands. Log-scale x-axis."""
    ...

def plot_efficiency_bar(
    efficiency_ratios: dict,  # {encoder: {zoo: float}}
    out_path: str,
) -> None:
    """Bar chart of efficiency ratios per (encoder, zoo). Dashed line at 2.0."""
    ...

def plot_seed_traces(
    results: dict,
    zoo_name: str,
    out_path: str,
) -> None:
    """Individual seed curves (alpha=0.2) + mean curve overlay."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: config, results_loader, analysis, visualize

```python
def main() -> None:
    """
    1. check_dwsnets_compatibility → update ENCODER_NAMES
    2. get_results() → results dict
    3. compute_all_efficiency_ratios → ratios
    4. verify_mechanism_activated for each equivariant encoder
    5. check_gate → log pass/fail
    6. plot_learning_curves for each zoo
    7. plot_efficiency_bar
    8. save results JSON to RESULTS_DIR/learning_curve_results.json
    9. print summary table
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Write config.py; resolve H-E1/H-M1 import paths; verify local ZOO_PATHS and MZDATASET_CODE_PATH resolve | 6 | 1+2+1+2 |
| A-2 | DWSNets Compatibility Check | Implement check_dwsnets_compatibility(); count FC layers in CNN-s zoo sample; log and exclude if <3 FC; document fallback in results JSON | 8 | 2+2+2+2 |
| A-3 | H-E1 Results Loader | Implement load_h_e1_results(); validate schema covers all (encoder, zoo, size) cells; return None if incomplete | 7 | 2+2+1+2 |
| A-4 | Training Fallback | Implement run_training_fallback(); wire H-E1 build_encoder/load_zoo/subsample/train_one/get_predictions for missing cells; 5-seed loop; batch_size=16 for N≤250 | 14 | 3+4+4+3 |
| A-5 | get_results Orchestration | Implement get_results(): check H-E1 JSON → fallback for gaps → merge; ensure results schema consistent regardless of path taken | 9 | 2+3+2+2 |
| A-6 | Bootstrap CI & Efficiency Ratio | Implement bootstrap_ci() and compute_efficiency_ratio(); handle edge case where encoder never reaches 90% peak (return inf); compute_all_efficiency_ratios() | 10 | 2+2+4+2 |
| A-7 | Gate & Mechanism Verification | Implement check_gate() and verify_mechanism_activated(); inherited equivariance sanity check (max_diff < 1e-4) on one test batch per equivariant encoder | 9 | 2+3+2+2 |
| A-8 | Visualization | Implement plot_learning_curves (CI bands, log-x), plot_efficiency_bar (≥2.0 threshold line), plot_seed_traces; save to figures/ | 10 | 2+1+4+3 |
| A-9 | Results JSON & Summary Table | Save full results JSON (schema: encoder→zoo→size→{mean_r2, ci_lo, ci_hi, seed_r2s}); print encoder|zoo|N_90|efficiency_ratio|gate table to stdout | 7 | 2+2+1+2 |
| A-10 | Integration & run_experiment.py | Wire all modules in main(); end-to-end test on cifar10 single encoder single size; verify no error path silently swallows DWSNets fallback | 12 | 2+4+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-6, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-9]

---

## Data Flow

- `run_experiment.py` → `results_loader.get_results()` → tries `h-e1/results/learning_curve_results.json`
  - Hit: returns dict directly (no training)
  - Miss: calls H-E1 `build_encoder`, `load_zoo`, `subsample`, `train_one`, `get_predictions` for each missing cell
- `analysis.compute_all_efficiency_ratios(results)` → `visualize.*` → JSON save

## Key Constraints

- H-E1 `config.py` has hardcoded absolute paths — H-M2 `config.py` must NOT import H-E1 config; import only H-E1 code modules
- `get_results()` merges H-E1 results + any fallback-trained cells so callers see uniform schema
- DWSNets excluded from ENCODER_NAMES at runtime if CNN-s zoo has ≤2 FC layers (per H-M1 caveat)
