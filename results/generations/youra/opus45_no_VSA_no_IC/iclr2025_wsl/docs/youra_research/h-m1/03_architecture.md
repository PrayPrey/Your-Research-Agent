# Architecture: H-M1 (NFN Equivariant Feature Extraction)

**Type**: MECHANISM | **Applied**: nn.Module composition pattern (PyTorch docs)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 provides data pipeline + baseline to reuse)
**Status**: Patterns found from base code — read directly via Read tool (Serena project not pre-activated for this path; direct file read used as equivalent MANDATORY analysis)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- H-E1 uses a **synthetic** Model Zoo (`data.py::generate_model_zoo`), not the real Zenodo download — `ResNet20` class defined locally, weights perturbed with accuracy-correlated noise, cached to `.pt`. H-M1 MUST reuse this same synthetic zoo (same cache file) for train/test parity with baseline.
- `data.py::split_test_set(items, test_size=500, seed=42)` — fixed split, MUST reuse identical seed for fair comparison.
- `features.py::build_feature_matrix` — 147-dim statistics (7 stats × 21 weight tensors), NOT 63 as brief states. Use actual baseline (`model.py::fit_ridge`, `evaluate`) as-is via import.
- Config constants live in flat `config.py` (no dataclass) — follow same style.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ResNet20 | `from h_e1.data import ResNet20` | `docs/youra_research/h-e1/code/data.py` |
| generate_model_zoo | `from h_e1.data import generate_model_zoo, load_checkpoints, split_test_set` | `docs/youra_research/h-e1/code/data.py` |
| build_feature_matrix | `from h_e1.features import build_feature_matrix` | `docs/youra_research/h-e1/code/features.py` |
| fit_ridge, evaluate | `from h_e1.model import fit_ridge, evaluate` | `docs/youra_research/h-e1/code/model.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not 03_architecture.md spec)

**Note**: Since Phase 4 code lives in a separate `h-m1/code/` folder, prefer **copying** `data.py`, `features.py`, `model.py`, `config.py` constants needed (small files) rather than cross-folder relative imports, to keep h-m1 self-contained. Epic A-1 handles this.

---

## Directory Structure

```
docs/youra_research/h-m1/code/
  config.py          # constants (extends h-e1 style)
  data.py             # copied from h-e1 (ResNet20, zoo gen/load/split)
  features.py         # copied from h-e1 (statistics baseline features)
  baseline_model.py   # copied from h-e1 (fit_ridge, evaluate) renamed to avoid clash
  nfn_adapter.py       # state_dict -> WeightSpaceFeatures conversion for ResNet20
  nfn_model.py         # NFNAccuracyPredictor
  equivariance.py       # permutation + verify_equivariance
  train.py              # training loop (NFN)
  evaluate.py            # R2/MAE/equivariance metrics + figures
  run_experiment.py       # orchestration entrypoint
  test_nfn_adapter.py       # 1 smoke test: shapes + equivariance on toy input
```

---

## Module Interfaces

### config.py (`code/config.py`)

**Dependencies**: none

```python
ZOO_DIR = "data/model_zoo"
TEST_SIZE = 500
SPLIT_SEED = 42
N_TRAIN = 5000
HIDDEN_DIM = 128
NUM_LAYERS = 3
LR = 1e-3
WEIGHT_DECAY = 1e-4
BATCH_SIZE = 32
EPOCHS = 100
EARLY_STOP_PATIENCE = 20
LR_PATIENCE = 10
SEEDS = [0, 1, 2]
EQUIVARIANCE_TOL = 1e-5
```

### data.py, features.py, baseline_model.py

Copied verbatim from H-E1 (see External Dependencies table). `baseline_model.py` = H-E1's `model.py` renamed.

### nfn_adapter.py (`code/nfn_adapter.py`)

**Dependencies**: nfn (official lib), data.ResNet20

```python
def resnet20_network_spec() -> "nfn.common.NetworkSpec": ...
def state_dicts_to_wsfeat(state_dicts: list[dict]) -> "WeightSpaceFeatures": ...
def collate_batch(items: list[tuple[dict, float]]) -> tuple["WeightSpaceFeatures", "torch.Tensor"]: ...
```

### nfn_model.py (`code/nfn_model.py`)

**Dependencies**: nfn_adapter

```python
class NFNAccuracyPredictor(nn.Module):
    def __init__(self, network_spec, hidden_dim: int = 128, num_layers: int = 3): ...
    def forward(self, weight_features: "WeightSpaceFeatures") -> "torch.Tensor": ...  # (B,1)
```

### equivariance.py (`code/equivariance.py`)

**Dependencies**: nfn_model

```python
def random_neuron_permutation(network_spec, seed: int) -> "Permutation": ...
def apply_permutation(wsfeat: "WeightSpaceFeatures", permutation) -> "WeightSpaceFeatures": ...
def verify_equivariance(nfn: nn.Module, wsfeat, permutation, atol: float = 1e-5) -> tuple[bool, float]: ...
def equivariance_pass_rate(nfn: nn.Module, test_items: list, network_spec, seed: int) -> float: ...
```

### train.py (`code/train.py`)

**Dependencies**: nfn_model, nfn_adapter, config

```python
def train_nfn(model: nn.Module, train_items: list, val_items: list, cfg=config) -> dict: ...  # returns history
def make_optimizer_scheduler(model, cfg=config): ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: sklearn.metrics, equivariance, baseline_model

```python
def evaluate_nfn(model, test_items) -> dict:  # {r2, mae, y_true, y_pred}
def evaluate_baseline(ridge_model, X_test, y_test) -> dict: ...
def plot_gate_comparison(nfn_r2: float, baseline_r2: float, out_path: str) -> None: ...
def plot_prediction_scatter(y_true, y_pred, r2: float, out_path: str) -> None: ...
def plot_equivariance(original_out, permuted_out, out_path: str) -> None: ...
def plot_training_curve(history: dict, out_path: str) -> None: ...
def plot_residuals(y_true, y_pred, out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above

```python
def main(seeds: list[int] = config.SEEDS) -> dict: ...  # orchestrates data->baseline->NFN->eval->figures->results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Bootstrap module | Copy/adapt H-E1 data.py, features.py, baseline_model.py, config.py into h-m1/code | 5 | 2+1+1+1 |
| A-2 | Install nfn + verify import | pip install nfn, smoke-test WeightSpaceFeatures/state_dict_to_tensors on ResNet20 | 4 | 1+1+1+1 |
| A-3 | Build ResNet20 network_spec | nfn_adapter: network_spec + state_dicts_to_wsfeat + collate_batch | 12 | 4+3+3+2 |
| A-4 | Implement NFNAccuracyPredictor | nfn_model.py using NFNBuilder, invariant_output, linear head | 8 | 3+2+2+1 |
| A-5 | Implement equivariance verification | equivariance.py: permutation generation, apply_permutation, verify_equivariance, pass-rate over test set | 10 | 3+3+2+2 |
| A-6 | Training loop | train.py: Adam+ReduceLROnPlateau, early stopping, batch loop over WeightSpaceFeatures | 9 | 3+2+2+2 |
| A-7 | Baseline reproduction | Run RidgeCV on same train/test split for fair R² comparison (reuses H-E1 code) | 4 | 1+1+1+1 |
| A-8 | Evaluation metrics | evaluate.py: R2/MAE for NFN + baseline, equivariance pass rate aggregation | 6 | 2+2+1+1 |
| A-9 | Figures | 5 required plots (gate comparison, scatter, equivariance, training curve, residuals) | 7 | 2+2+2+1 |
| A-10 | Orchestration + smoke test | run_experiment.py multi-seed loop, results.json, test_nfn_adapter.py equivariance smoke test | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-7, A-8, A-9, A-10]

**Note**: A-3 (network spec construction for ResNet-20 in NFN's expected format, including BatchNorm/skip-connection handling) is the highest-risk task — NFN's official CNN support targets simple conv stacks; ResNet skip connections may need `nfn`'s residual-aware layers or custom spec. Flag for Phase 4 investigation of `examples/basic_cnn/` in the nfn repo.
