---
hypothesis_id: h-m3
phase: architecture
generated_at: "2026-08-21"
---

# Architecture: H-M3 — Permutation Augmentation (PermAug) for Flat-MLP

Applied: wrapper-dataset augmentation pattern (Archon KB: no relevant hits — domain mismatch confirmed)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis + existing_codebase
**Status**: Read directly via file tools (Serena requires project activation; bypassed with direct reads)
**Analyzed Path**: `docs/youra_research/h-m2/code/` and `docs/youra_research/h-e1/code/`
**Findings**:
- H-M2 code contains: `config.py`, `results_loader.py`, `analysis.py`, `visualize.py`, `run_experiment.py`
- H-E1 code contains: `config.py`, `data.py`, `encoders.py`, `train.py`, `evaluate.py`, `visualize.py`, `run_experiment.py`
- H-M2 `results_loader.py` imports `config as cfg` — H-M3 must provide compatible `config.py`
- H-M2 `analysis.py` imports `config as cfg` — same constraint
- H-M2 `config.py` sets `H_E1_CODE_DIR`, `H_M1_CODE_DIR`, `H_E1_RESULTS_JSON`, `ZOO_PATHS`, `MZDATASET_CODE_PATH`
- Training loop in H-M2 is via `results_loader.run_training_fallback` which calls H-E1's `train.py:train_one`
- H-M3 does NOT reuse `run_training_fallback` — trains only PermAug fresh, loads the rest from stored JSON

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_h_e1_results | `from results_loader import load_h_e1_results` | `h-m2/code/results_loader.py` |
| bootstrap_ci | `from analysis import bootstrap_ci` | `h-m2/code/analysis.py` |
| FlatMLP / FlatCollator / load_zoo / subsample | `from data import ...` | `h-e1/code/data.py` |
| train_one / get_predictions | `from train import train_one, get_predictions` | `h-e1/code/train.py` |

**Verified from**: `docs/youra_research/h-m2/code/` and `docs/youra_research/h-e1/code/` (actual files)

---

## File Structure

- `code/config.py` — all hyperparameters and paths
- `code/perm_aug.py` — PermAugDataset + apply_random_permutation
- `code/verify.py` — mechanism verification (must run before training)
- `code/train.py` — PermAug-only training loop (4 runs × N)
- `code/results_loader.py` — load Flat-MLP and GNN-NFN from H-E1/H-M2
- `code/analysis.py` — bootstrap CI, gap analysis, gate check (thin wrappers + gap computation)
- `code/visualize.py` — 4 required figures
- `code/run_experiment.py` — orchestrator

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: os only

```python
# Paths
H_E1_CODE_DIR: str       # docs/youra_research/h-e1/code
H_M2_CODE_DIR: str       # docs/youra_research/h-m2/code
H_E1_RESULTS_JSON: str   # docs/youra_research/h-e1/results/results.json
H_M2_RESULTS_JSON: str   # docs/youra_research/h-m2/results/results.json
H_M1_CODE_DIR: str       # docs/youra_research/h-m1/code (for H-E1 import chain)
MZDATASET_CODE_PATH: str # path to ModelZooDataset code
ZOO_PATHS: dict          # {"cifar10": "<local path>"}
FIGURES_DIR: str
RESULTS_DIR: str

# Hyperparameters (all match H-E1/H-M2)
SEED: int = 42
EPOCHS: int = 100
BATCH_SIZE: int = 64
BATCH_SIZE_SMALL: int = 16
SMALL_SIZE_THRESHOLD: int = 250
LR: float = 1e-3
WEIGHT_DECAY: float = 1e-4
N_BOOT: int = 1000
CI_LEVEL: float = 0.95

# Experiment scope
TRAINING_SIZES: list = [100, 250, 500, 1000]
ZOO_NAMES: list = ["cifar10"]
NUM_PERMUTATIONS: int = 10
PRIMARY_BUDGET: int = 200_000
ZOO_ARCH: str = "cnn"
GNN_HIDDEN_DIM: int = 64
GNN_NUM_LAYERS: int = 4
```

---

### PermAugDataset (`code/perm_aug.py`)

**Dependencies**: torch, config

```python
def apply_random_permutation(weight_vector: Tensor, layer_sizes: list[int]) -> Tensor:
    """Permute hidden-layer neurons per Zhou 2023 (NFN Eq. 1).
    For each hidden layer l: W_l[perm,:], b_l[perm], W_{l+1}[:,perm].
    layer_sizes: [input, h1, h2, ..., output] (includes bias).
    Returns permuted flat vector, same shape as input."""
    ...

class PermAugDataset(torch.utils.data.Dataset):
    def __init__(self, base_dataset: Dataset, layer_sizes: list[int],
                 num_permutations: int = 10): ...
    def __len__(self) -> int: ...          # len(base) * (num_permutations + 1)
    def __getitem__(self, idx: int) -> tuple[Tensor, Tensor]: ...
    # aug_idx==0 → original; aug_idx>0 → apply_random_permutation(x, layer_sizes)

def get_layer_sizes(zoo_path: str) -> list[int]:
    """Extract [input, h1, ..., output] from ModelZooDataset index_dict or first sample."""
    ...
```

---

### Verify (`code/verify.py`)

**Dependencies**: perm_aug, config, torch

```python
def verify_perm_aug_activated(x: Tensor, layer_sizes: list[int]) -> float:
    """Returns aug_diff = (apply_random_permutation(x) - x).abs().max().
    Asserts diff > 1e-6. Prints [H-M3 MECHANISM CHECK] line."""
    ...

def verify_perm_aug_mechanism(
    perm_dataset: PermAugDataset,
    plain_dataset: Dataset,
    layer_sizes: list[int],
) -> dict:
    """Runs 2 checks:
      1. aug_diff > 1e-6 (permutation changes tensor)
      2. len(perm_dataset) == len(plain_dataset) * (NUM_PERMUTATIONS + 1)
    Prints all indicators. Raises RuntimeError if any check fails.
    Returns indicators dict."""
    ...
```

---

### ResultsLoader (`code/results_loader.py`)

**Dependencies**: config, sys (H-M2 results_loader for load_h_e1_results)

```python
def load_baselines(h_e1_json: str, h_m2_json: str) -> dict:
    """Load flat_mlp from H-E1 and gnn_nfn from H-M2 results.
    Returns {encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi, seed_r2s}}}}.
    Raises FileNotFoundError with explicit message if either file missing.
    Does NOT re-train anything."""
    ...

def save_perm_aug_results(perm_aug_r2s: dict, baselines: dict, out_path: str) -> dict:
    """Merge perm_aug_r2s into baselines, save JSON to out_path.
    perm_aug_r2s: {zoo: {str(size): {mean_r2, ci_lo, ci_hi, seed_r2s}}}.
    Returns merged results dict."""
    ...
```

---

### Train (`code/train.py`)

**Dependencies**: config, perm_aug, verify, torch, sklearn

```python
def train_perm_aug(
    n_train: int,
    zoo_name: str = "cifar10",
    device: str = "cuda",
) -> tuple[float, list[float], list[float]]:
    """Train FlatMLP + PermAug for one (zoo, n_train) cell.
    - Loads data via H-E1 data.load_zoo + subsample (seed=cfg.SEED)
    - Wraps train split in PermAugDataset
    - Calls verify.verify_perm_aug_mechanism BEFORE training (raises on fail)
    - Trains cfg.EPOCHS epochs, Adam lr=cfg.LR, wd=cfg.WEIGHT_DECAY
    - Test eval uses plain (non-augmented) weights
    Returns (r2_test, train_loss_curve, val_loss_curve)."""
    ...

def train_all_sizes(
    sizes: list[int],
    zoo_name: str = "cifar10",
    device: str = "cuda",
) -> dict:
    """Train PermAug for all N in sizes. Returns {str(N): {r2, train_losses, val_losses}}."""
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: numpy, config

```python
def bootstrap_ci(r2_values: list[float], n_boot: int = 1000) -> tuple[float, float, float]:
    """Percentile bootstrap CI. Returns (mean, ci_lo, ci_hi).
    Delegates to H-M2 analysis.bootstrap_ci if len < 2."""
    ...

def compute_gap_analysis(results: dict, zoo: str = "cifar10") -> dict:
    """For each training size:
      gap_total = R²(gnn_nfn) - R²(flat_mlp)
      gap_perm_aug = R²(flat_mlp_perm_aug) - R²(flat_mlp)
      perm_aug_fraction = gap_perm_aug / gap_total
    Returns {str(N): {gap_total, gap_perm_aug, perm_aug_fraction}}."""
    ...

def check_ordering_gate(results: dict, zoo: str = "cifar10",
                         gate_sizes: list[int] = [100, 250]) -> tuple[bool, dict]:
    """Strict ordering check with non-overlapping bootstrap CIs at gate_sizes.
    flat_mlp CI_hi < perm_aug CI_lo AND perm_aug CI_hi < gnn_nfn CI_lo.
    Returns (gate_passed, details)."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, config

```python
def plot_gate_metrics(results: dict, out_path: str) -> None:
    """Bar chart: R² at N=100,250 for 3 encoders with bootstrap 95% CI error bars.
    Saves to figures/gate_metrics.png."""
    ...

def plot_ordering_curve(results: dict, out_path: str) -> None:
    """Line plot: R² vs N for all 3 conditions with CI bands.
    Saves to figures/ordering_plot.png."""
    ...

def plot_gap_fraction(gap_analysis: dict, out_path: str) -> None:
    """Bar chart: perm_aug_fraction at N=100,250 with horizontal bands at 0.5 and 0.8.
    Saves to figures/gap_fraction.png."""
    ...

def plot_training_curves(train_curves: dict, out_path: str) -> None:
    """Line plot: training loss for flat_mlp vs flat_mlp_perm_aug.
    train_curves: {encoder: list[float]} for 1 or more N.
    Saves to figures/training_curves.png."""
    ...
```

---

### Orchestrator (`code/run_experiment.py`)

**Dependencies**: all above modules, config

```python
def main(device: str = "cuda") -> None:
    """
    1. Load baselines (flat_mlp from H-E1, gnn_nfn from H-M2) — raise if missing
    2. Train PermAug at N in cfg.TRAINING_SIZES (verify mechanism before each run)
    3. Compute bootstrap CI for perm_aug results
    4. Merge all results and save results/results.json
    5. Run gap analysis and gate check
    6. Generate 4 figures
    7. Print summary table
    """
    ...

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cuda")
    args = p.parse_args()
    main(args.device)
```

---

## Data Flow

- `run_experiment.py` → `results_loader.load_baselines()` → H-E1/H-M2 JSON files
- `run_experiment.py` → `train.train_all_sizes()`:
  - → `verify.verify_perm_aug_mechanism()` (MUST pass before training)
  - → H-E1 `data.load_zoo()` + `data.subsample()`
  - → `perm_aug.PermAugDataset` wraps train split
  - → H-E1 `encoders.build_encoder("flat_mlp", ...)` + H-E1 `train.train_one()`
  - → H-E1 `train.get_predictions()` on plain test set → `r2_score`
- `run_experiment.py` → `analysis.bootstrap_ci()` → `analysis.check_ordering_gate()`
- `run_experiment.py` → `results_loader.save_perm_aug_results()` → `results/results.json`
- `run_experiment.py` → `visualize.*` → `figures/*.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | config.py with all paths/hyperparams; wire H-E1/H-M2 code dirs into sys.path | 5 | 1+1+1+2 |
| A-2 | PermAug core | apply_random_permutation + PermAugDataset + get_layer_sizes | 13 | 3+2+4+4 |
| A-3 | Mechanism verify | verify_perm_aug_activated + verify_perm_aug_mechanism; must raise on failure | 8 | 2+2+2+2 |
| A-4 | Results loader | load_baselines (H-E1 + H-M2 JSON); save_perm_aug_results; no re-training | 8 | 2+3+2+1 |
| A-5 | Training loop | train_perm_aug + train_all_sizes; calls verify before training; plain test eval | 12 | 3+3+3+3 |
| A-6 | Analysis | bootstrap_ci + compute_gap_analysis + check_ordering_gate | 9 | 2+2+3+2 |
| A-7 | Visualization | 4 figures (gate_metrics, ordering_plot, gap_fraction, training_curves) | 8 | 2+1+2+3 |
| A-8 | Orchestrator | run_experiment.py wiring all steps; argparse; summary table print | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5, A-6], Low(4-8): [A-1, A-3, A-4, A-7, A-8]

---

## Results Schema (`results/results.json`)

```json
{
  "flat_mlp":          {"cifar10": {"100": {"mean_r2": -0.141, "ci_lo": ..., "ci_hi": ...}, ...}},
  "flat_mlp_perm_aug": {"cifar10": {"100": {"mean_r2": ...,    "ci_lo": ..., "ci_hi": ...}, ...}},
  "gnn_nfn":           {"cifar10": {"100": {"mean_r2": -0.016, "ci_lo": ..., "ci_hi": ...}, ...}},
  "gap_analysis":      {"100": {"gap_total": ..., "gap_perm_aug": ..., "perm_aug_fraction": ...}, ...},
  "gate": {"satisfied": true, "result_str": "..."}
}
```
