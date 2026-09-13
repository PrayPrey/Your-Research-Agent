# Architecture: H-E1
# Equivariant Weight-Space Encoders — Sample Efficiency PoC

---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-21
author: yoon303@etri.re.kr

---

Applied: No KB pattern applicable (Archon KB contains diffusion models only; similarity 0.38–0.49 to irrelevant content)

---

## Codebase Analysis (Serena)

**Green-field project** — no existing codebase to analyze.

This is a new experiment from scratch. External repos (DWSNets, neural-graphs, nfn, ModelZooDataset) are treated as installed dependencies; their APIs are documented in the experiment brief (02c_experiment_brief.md). No Serena analysis performed — there is no local source tree to traverse.

External dependency APIs verified from GitHub README and paper implementations:
- `AvivNavon/DWSNets`: `MLPModelForRegression(weight_shapes, hidden_dim)` — structured matrix input
- `mkofinas/neural-graphs`: `GNNForRegression` — PyG graph batch input
- `AllanYangZhou/nfn`: `NPLinear(network_spec, in_ch, out_ch) + HNPPool` — CNN zoo fallback
- `ModelZoos/ModelZooDataset`: `torch.load(zoo_path)` — returns object with `.weights`, `.metrics`

---

## 1. Overview / Design Principles

Single experiment script with minimal supporting modules. Four encoder conditions
(Flat-MLP, Flat-MLP+PermAug, DWSNets/NFN, GNN-NFN) share one training loop,
one evaluation function, one config. All results for both zoos × 5 training sizes
accumulate in a single results dict and are written once.

External repos (DWSNets, neural-graphs, nfn, ModelZooDataset) are treated as
installed libraries — imported, not re-implemented.

---

## 2. Module Structure

```
h-e1/
  code/
    config.py          # all hyperparameters and paths
    data.py            # ModelZooDataset loading + subsampling + preprocessing
    encoders.py        # FlatMLP, FlatMLPPermAug, DWSNetEncoder, GNNNFNEncoder
    train.py           # shared training loop
    evaluate.py        # R², bootstrap CI, mechanism verification
    visualize.py       # Figures 1-4
    run_experiment.py  # orchestration: conditions × training sizes × zoos
  figures/             # output figures (git-ignored)
  results/             # output JSON (git-ignored)
```

---

## 3. Module Descriptions

### Config (`code/config.py`)

**Dependencies**: none

```python
# All values are plain constants — no argparse, no hydra for PoC
SEED: int = 42
EPOCHS: int = 200
BATCH_SIZE: int = 64
LR: float = 1e-3
WEIGHT_DECAY: float = 1e-4
N_BOOTSTRAP: int = 1000
TRAINING_SIZES: list[int | str] = [100, 250, 500, 1000, "full"]
BUDGET_TIERS: dict[str, int] = {"small": 50_000, "medium": 200_000, "large": 500_000}
ZOO_NAMES: list[str] = ["mnist", "cifar10"]
ZOO_PATHS: dict[str, str]   # absolute paths to .pt files
FIGURES_DIR: str
RESULTS_DIR: str
ENCODER_NAMES: list[str] = ["flat_mlp", "flat_mlp_perm_aug", "dwsnet", "gnn_nfn"]
```

---

### Data (`code/data.py`)

**Dependencies**: config, ModelZooDataset repo, torch

```python
def load_zoo(zoo_name: str) -> tuple[object, object, object]:
    """Returns (train_dataset, val_dataset, test_dataset) from .pt file."""
    ...

def diversity_check(test_dataset: object) -> dict[str, float]:
    """Returns {"variance": float, "passed": bool}. Logs warning if variance < 0.05."""
    ...

def subsample(dataset: object, n: int | str, seed: int = 42) -> object:
    """Returns subsampled dataset. n='full' returns dataset unchanged."""
    ...

def make_flat_loader(dataset: object, batch_size: int, shuffle: bool) -> DataLoader:
    """Flattens weights+biases, standardizes (fit on train), returns DataLoader."""
    ...

def make_structured_loader(dataset: object, batch_size: int, shuffle: bool,
                           for_gnn: bool = False) -> DataLoader:
    """Keeps weights as structured matrices. for_gnn=True returns PyG graphs."""
    ...

def detect_zoo_arch(dataset: object) -> str:
    """Returns 'mlp' or 'cnn'. Used to select DWSNets vs NFN fallback."""
    ...
```

---

### Encoders (`code/encoders.py`)

**Dependencies**: config, torch, DWSNets repo, nfn repo, neural-graphs repo

```python
class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor: ...           # (B,) scalar

class FlatMLPPermAug(FlatMLP):
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int = 3,
                 perm_prob: float = 0.5): ...
    def forward(self, weights: list[Tensor], biases: list[Tensor],
                training: bool = False) -> Tensor: ...    # applies perm aug when training=True

class DWSNetEncoder(nn.Module):
    """Wraps MLPModelForRegression (DWSNets repo) or NPLinear+HNPPool (nfn repo)."""
    def __init__(self, weight_shapes: list[tuple], hidden_dim: int,
                 zoo_arch: str = "cnn"): ...              # selects DWSNets vs NFN path
    def forward(self, weights: list[Tensor], biases: list[Tensor]) -> Tensor: ...
    def count_params(self) -> int: ...

class GNNNFNEncoder(nn.Module):
    """Wraps GNNForRegression from neural-graphs repo."""
    def __init__(self, weight_shapes: list[tuple], hidden_dim: int): ...
    def forward(self, graph_batch: "torch_geometric.data.Batch") -> Tensor: ...
    def count_params(self) -> int: ...

def build_encoder(name: str, weight_shapes: list[tuple], target_params: int,
                  zoo_arch: str) -> nn.Module:
    """Grid-searches hidden_dim to hit target_params within ±20%, returns encoder."""
    ...
```

---

### Training (`code/train.py`)

**Dependencies**: config, encoders, data, torch

```python
def train_one(
    encoder: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = 200,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    seed: int = 42,
) -> dict[str, list[float]]:
    """
    Adam + CosineAnnealingLR + MSE. Returns {"train_loss": [...], "val_loss": [...]}.
    Encoder type detected from isinstance checks for structured vs flat forward call.
    """
    ...
```

---

### Evaluation (`code/evaluate.py`)

**Dependencies**: config, sklearn, numpy, torch

```python
def get_predictions(encoder: nn.Module, loader: DataLoader) -> tuple[np.ndarray, np.ndarray]:
    """Returns (y_true, y_pred) arrays on the fixed test set."""
    ...

def compute_r2_with_ci(
    y_true: np.ndarray, y_pred: np.ndarray, n_bootstrap: int = 1000
) -> dict[str, float]:
    """Returns {"r2": float, "ci_low": float, "ci_high": float}."""
    ...

def verify_equivariance(encoder: nn.Module, sample_weights: list[Tensor],
                        sample_biases: list[Tensor], tol: float = 1e-4) -> bool:
    """Permutes neurons, checks |output_perm - output_orig| < tol."""
    ...

def diversity_report(zoo_name: str, test_dataset: object) -> dict[str, float]:
    """Wraps data.diversity_check; returns variance + pass/fail."""
    ...
```

---

### Visualization (`code/visualize.py`)

**Dependencies**: config, matplotlib, numpy

```python
def fig1_bar_chart(results: dict, zoo_name: str, training_size: int = 500) -> None:
    """R² bar chart with 95% CI, all 4 conditions. Saved to FIGURES_DIR."""
    ...

def fig2_learning_curves(results: dict, zoo_name: str) -> None:
    """R² vs training size lines, all 4 conditions. Saved to FIGURES_DIR."""
    ...

def fig3_ci_overlap(results: dict, zoo_name: str) -> None:
    """CI band plot: equivariant vs Flat-MLP per training size. Saved to FIGURES_DIR."""
    ...

def fig4_diversity_histogram(test_dataset: object, zoo_name: str) -> None:
    """Histogram of test-accuracy distribution. Saved to FIGURES_DIR."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """
    Outer loop: zoo_name × training_size × encoder_name × budget_tier
    Calls: load_zoo → diversity_check → subsample → build_encoder
           → train_one → get_predictions → compute_r2_with_ci
    Writes results dict to RESULTS_DIR/results.json after all conditions.
    Calls all four fig* functions per zoo.
    Logs equivariance verification per equivariant encoder.
    """
    ...

if __name__ == "__main__":
    main()
```

---

## 4. Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. External repos (DWSNets, neural-graphs, nfn, ModelZooDataset) imported as dependencies; not analyzed via Serena.

---

## 5. Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| A-1 | Data Pipeline | Implement data.py: load zoo .pt files, diversity check, subsampling, flat/structured loaders, CNN/MLP arch detection | data.py | 10 | 3+2+2+3 |
| A-2 | Baseline Encoders | Implement FlatMLP and FlatMLPPermAug in encoders.py; param-budget grid search in build_encoder | encoders.py | 8 | 2+1+2+3 |
| A-3 | Equivariant Encoders | Wrap DWSNets/NFN and GNN-NFN in encoders.py; CNN fallback logic; equivariance verification | encoders.py, evaluate.py | 14 | 3+4+4+3 |
| A-4 | Training Loop | Shared train_one() with Adam+CosineAnnealingLR+MSE; structured vs flat dispatch | train.py | 8 | 2+2+2+2 |
| A-5 | Evaluation | R² + bootstrap CI, equivariance test, diversity report | evaluate.py | 8 | 2+2+2+2 |
| A-6 | Orchestration + Viz | run_experiment.py full loop; all 4 figures; JSON results write | run_experiment.py, visualize.py | 12 | 3+3+2+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-6, A-1], Low(4-8): [A-2, A-4, A-5]

---

## 6. External Dependencies

| Package / Repo | Import Path | Purpose |
|----------------|-------------|---------|
| AvivNavon/DWSNets | `from nn.dws.models import MLPModelForRegression` | Equivariant encoder (MLP zoo path) |
| AllanYangZhou/nfn | `from nfn.layers import NPLinear, HNPPool` | Equivariant encoder (CNN zoo fallback) |
| mkofinas/neural-graphs | `from nn.gnn import GNNForRegression` | GNN-NFN encoder |
| ModelZoos/ModelZooDataset | dataset class in `code/checkpoints_to_datasets/dataset_base.py` | Zoo loading |
| torch-geometric | `from torch_geometric.data import Batch` | GNN-NFN graph batching |
| sklearn | `from sklearn.metrics import r2_score` | R² metric |
| scipy / numpy | bootstrap resampling | CI computation |
| matplotlib | figure generation | Figures 1-4 |

**Note**: All three equivariant repos must be cloned and installed (`pip install -e .`) before running. Data files require manual Zenodo download.
