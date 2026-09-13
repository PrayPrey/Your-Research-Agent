# Architecture: H-M1 (Weight Matrices Encode Behavioral Information)

**Type:** MECHANISM | **Tier:** STANDARD

Applied: linear-probe-mechanism-test pattern (extract features -> fit probe -> compare vs baseline -> gate)
Applied: weight-statistics-extraction pattern (per-layer mean/std/min/max/norm, Unterthiner et al. 2020)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** patterns found from base code — Serena MCP tool call failed (no active project registered for this path); performed equivalent manual analysis via direct file reads of `h-e1/code/`.
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:**
- Real model zoo entries are **`OrderedDict` state_dicts** (5 weight tensors: `module_list.{0,3,6,9,11}.weight`), NOT a flat `(N, 4970)` array as PRD/brief assumed. PRD/brief specs (flat `cifar10_weights.npy`, `metrics.csv.gz`) do not match actual data format — actual code trusted over spec.
- Actual usable sample: **n_models=193** (from `outputs/results.json`), far below the "~30k" claimed in PRD FR-1. Only final-epoch models with parseable architecture were retained.
- `model_zoo_loader.py` already implements `load_model_zoo_final_epoch()` (returns `(model_id, state_dict, test_acc)` list) and `get_model_predictions_from_weights()` — reused as-is for H-M1.
- `analysis.py` already implements `compute_class_wise_accuracy()` and `stratified_baseline()` — reused as-is; H-M1 baseline is identical to H-E1 baseline.
- `config.py` `CIFAR_ROOT` hardcodes an absolute path from a different experiment run; H-M1 config must repoint or reuse relative `code/data`.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_model_zoo_final_epoch | `from base.model_zoo_loader import load_model_zoo_final_epoch` | `h-e1/code/model_zoo_loader.py` |
| get_model_predictions_from_weights | `from base.model_zoo_loader import get_model_predictions_from_weights` | `h-e1/code/model_zoo_loader.py` |
| compute_class_wise_accuracy | `from base.analysis import compute_class_wise_accuracy` | `h-e1/code/analysis.py` |
| stratified_baseline | `from base.analysis import stratified_baseline` | `h-e1/code/analysis.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not 03_architecture.md spec)

**Note**: Copy the four base files (`model_zoo_loader.py`, `analysis.py`, `data.py`, plus CIFAR-10 cached data dir) into `h-m1/code/base/` rather than cross-repo import, since h-e1 is a sibling hypothesis folder, not an installable package.

## File Structure

- `base/model_zoo_loader.py` - copied from h-e1 (unchanged)
- `base/analysis.py` - copied from h-e1 (unchanged)
- `weight_features.py` - per-layer weight statistics extraction (NEW, core mechanism)
- `probe.py` - Ridge probe: baseline vs proposed models (NEW)
- `visualize.py` - gate comparison + optional figures (NEW)
- `config.py` - fixed constants, paths
- `run.py` - orchestration

## Modules

### config.py

```python
SEED = 42
N_CLASSES = 10
TEST_SPLIT = 0.2
RIDGE_ALPHA = 1.0
DATA_PATH = "./base/data/dataset_cifar_small_hyp_rand.pt"
CIFAR_ROOT = "./base/data"
FIGURES_DIR = "./figures"
RESULTS_PATH = "./outputs/results.json"
```

### weight_features.py

**Dependencies**: numpy, torch

```python
LAYER_KEYS = [
    "module_list.0.weight", "module_list.3.weight",
    "module_list.6.weight", "module_list.9.weight", "module_list.11.weight",
]

def extract_layer_statistics(state_dict: dict) -> np.ndarray:
    # returns (25,) vector: 5 layers x [mean, std, min, max, norm]
    ...

def build_weight_feature_matrix(model_entries: list) -> tuple[np.ndarray, list[str]]:
    # model_entries: [(model_id, state_dict, test_acc), ...]
    # returns features (N, 25), model_ids
    ...
```

### probe.py

**Dependencies**: sklearn.linear_model.Ridge, sklearn.preprocessing.StandardScaler, sklearn.metrics.r2_score, weight_features

```python
def train_test_split_indices(n: int, test_frac: float, seed: int) -> tuple[np.ndarray, np.ndarray]: ...

def fit_stratified_baseline(overall_acc, class_difficulty, class_wise_acc, train_idx) -> Ridge: ...
    # reuses base.analysis.stratified_baseline for class_difficulty

class WeightToClassAccuracyProbe:
    def __init__(self, alpha: float = 1.0): ...
    def fit(self, weight_features: np.ndarray, class_accuracies: np.ndarray) -> None: ...
    def predict(self, weight_features: np.ndarray) -> np.ndarray: ...

def evaluate_r2(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[list[float], float]:
    # returns per_class_r2, mean_r2
    ...

def run_gate_comparison(
    weight_features, class_wise_acc, overall_acc, train_idx, test_idx
) -> dict:
    # returns {"baseline_r2_mean", "proposed_r2_mean", "baseline_r2_per_class", "proposed_r2_per_class", "gate_pass"}
    ...
```

### visualize.py

**Dependencies**: matplotlib

```python
def plot_gate_metric(baseline_r2: float, proposed_r2: float, out_path: str) -> str: ...
def plot_per_class_r2_comparison(baseline_per_class: list, proposed_per_class: list, out_path: str) -> str: ...
def plot_predicted_vs_actual(y_true: np.ndarray, y_pred: np.ndarray, class_idx: int, out_path: str) -> str: ...
```

### run.py

**Dependencies**: config, base.model_zoo_loader, base.analysis, weight_features, probe, visualize, json

```python
def main() -> None:
    # load model_entries -> predictions -> class_wise_acc/overall_acc (base.analysis)
    # -> weight features (weight_features) -> split -> baseline vs proposed (probe)
    # -> gate check -> figures -> results.json
    ...

def build_report(gate_result: dict, figure_paths: list, n_models: int) -> dict:
    # {"pass": bool, "metrics": {...}, "figures": [...]}
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Port base modules | Copy model_zoo_loader.py, analysis.py, cached CIFAR data from h-e1 | 5 | 2+1+1+1 |
| M-2 | Load model zoo + predictions | Run load_model_zoo_final_epoch + inference pipeline (n≈193) | 6 | 2+2+2+0 |
| M-3 | Class-wise accuracy + baseline features | Reuse compute_class_wise_accuracy, stratified_baseline for class_difficulty | 5 | 1+2+2+0 |
| M-4 | Weight statistics extraction | Implement extract_layer_statistics over 5 real layer tensors (25 features) | 9 | 3+2+3+1 |
| M-5 | Train/test split | Fixed-seed 80/20 split shared across baseline & proposed | 4 | 1+1+1+1 |
| M-6 | Baseline Ridge probe | Fit/predict stratified baseline (overall_acc + class_difficulty) | 6 | 2+2+2+0 |
| M-7 | Proposed Ridge probe | StandardScaler + Ridge on weight features, predict 10-class accuracy | 7 | 2+2+3+0 |
| M-8 | R² evaluation + gate check | Per-class + mean R², proposed_R2 > baseline_R2 assertion | 6 | 1+2+2+1 |
| M-9 | Required visualization | Gate metrics comparison bar chart (proposed vs baseline R²) | 4 | 1+1+1+1 |
| M-10 | Optional visualizations | Predicted-vs-actual scatter, per-class R² bar chart | 6 | 2+1+2+1 |
| M-11 | Orchestration + reporting | run.py pipeline, results.json, pass/fail gate output | 6 | 2+3+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-4], Low(4-8): [M-1, M-2, M-3, M-5, M-6, M-7, M-8, M-9, M-10, M-11]
