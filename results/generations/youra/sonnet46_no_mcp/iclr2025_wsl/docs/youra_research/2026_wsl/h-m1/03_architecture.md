# Architecture: H-M1 — Flat MLP Encoder Permutation Sensitivity Probing

**Applied**: flat-MLP-weight-space-encoder pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260505_wsl/h-e1/code/`
**Findings**: h-e1 uses flat local imports (`from config import ExperimentConfig`); all modules in `code/` directory with no package `__init__.py`. `stratified_pair_sample` returns `List[Tuple[Dict, Dict, int]]`. `load_zoo_checkpoints` uses `ExperimentConfig` as argument. `flatten_weights` handles `_flat_weights` pre-vectorized format from Zenodo dataset.

---

## External Dependencies (Base Hypothesis)

| Module | Function | File Location |
|--------|----------|---------------|
| `load_zoo_checkpoints` | `sys.path.insert` then `from data_loader import load_zoo_checkpoints` | `h-e1/code/data_loader.py` |
| `flatten_weights` | `from weight_analysis import flatten_weights` | `h-e1/code/weight_analysis.py` |
| `stratified_pair_sample` | `from weight_analysis import stratified_pair_sample` | `h-e1/code/weight_analysis.py` |
| `ExperimentConfig` | `from config import ExperimentConfig` (h-e1 config, for load_zoo_checkpoints arg) | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/20260505_wsl/h-e1/code/` (actual implementation)

**Import pattern** (h-e1 uses local imports, not installable package):
```python
import sys
HE1_CODE = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(HE1_CODE))
from data_loader import load_zoo_checkpoints
from weight_analysis import flatten_weights, stratified_pair_sample
```

---

## File Structure

- `h-m1/code/config.py` — ExperimentConfig for h-m1
- `h-m1/code/data_loader.py` — dataset loading + normalization
- `h-m1/code/models.py` — FlatMLPEncoder + width grid search
- `h-m1/code/train.py` — training loop
- `h-m1/code/probe.py` — permutation generation + sensitivity scoring
- `h-m1/code/evaluate.py` — Spearman ρ + gate check
- `h-m1/code/visualize.py` — all 5 required figures
- `h-m1/code/run_experiment.py` — main entry point
- `h-m1/figures/` — output figures

---

## Module Definitions

### ExperimentConfig (`h-m1/code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

@dataclass
class ExperimentConfig:
    # Data
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # Model
    embed_dim: int = 128
    dropout: float = 0.1
    target_params_min: int = 475_000
    target_params_max: int = 525_000
    hidden_dims_candidates: List[List[int]] = field(default_factory=lambda: [
        [9], [10], [8, 256], [8, 512], [16, 128], [16, 256]
    ])

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    sensitivity_gate: float = 0.3
    spearman_target: float = 0.5

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.he1_code_dir = Path(self.he1_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)
```

---

### WeightDataset (`h-m1/code/data_loader.py`)

**Dependencies**: ExperimentConfig, h-e1/load_zoo_checkpoints, h-e1/flatten_weights

```python
from typing import Dict, List, Optional, Tuple
import torch
from torch.utils.data import Dataset, DataLoader

class WeightDataset(Dataset):
    def __init__(
        self,
        checkpoints: List[Dict],
        mean: Optional[torch.Tensor] = None,
        std: Optional[torch.Tensor] = None,
    ): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]: ...
    # Returns (normalized_flat_weight, accuracy_scalar)

def load_and_split_dataset(cfg: "ExperimentConfig") -> Tuple[
    WeightDataset, WeightDataset, WeightDataset,
    torch.Tensor, torch.Tensor,  # train_mean, train_std
    List[Dict],                   # all_checkpoints (for probing)
]:
    """Load zoo, apply Schurholt splits, z-score normalize from train set."""
    ...

def build_dataloaders(
    train_ds: WeightDataset,
    val_ds: WeightDataset,
    test_ds: WeightDataset,
    cfg: "ExperimentConfig",
) -> Tuple[DataLoader, DataLoader, DataLoader]: ...
```

---

### FlatMLPEncoder (`h-m1/code/models.py`)

**Dependencies**: ExperimentConfig

```python
import torch
import torch.nn as nn
from typing import List, Tuple

class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int], embed_dim: int = 128, dropout: float = 0.1): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
    # Input: (B, input_dim) → Output: (B, embed_dim)

class FlatMLPWithHead(nn.Module):
    """Encoder + linear prediction head for training."""
    def __init__(self, encoder: FlatMLPEncoder, embed_dim: int = 128): ...
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]: ...
    # Returns (embedding (B, embed_dim), prediction (B, 1))

def grid_search_architecture(
    input_dim: int,
    candidates: List[List[int]],
    embed_dim: int,
    dropout: float,
    target_min: int,
    target_max: int,
) -> Tuple[FlatMLPEncoder, List[int], int]:
    """Iterate candidates; return first encoder within param budget."""
    ...

def count_params(model: nn.Module) -> int: ...
```

---

### Trainer (`h-m1/code/train.py`)

**Dependencies**: FlatMLPWithHead, WeightDataset, ExperimentConfig

```python
from dataclasses import dataclass, field
from typing import Dict, List
import torch
from torch.utils.data import DataLoader

@dataclass
class TrainHistory:
    train_loss: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    train_spearman: List[float] = field(default_factory=list)
    val_spearman: List[float] = field(default_factory=list)

def train_encoder(
    model: "FlatMLPWithHead",
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: "ExperimentConfig",
    device: torch.device,
) -> Tuple["FlatMLPWithHead", TrainHistory]:
    """Adam + CosineAnnealingLR; logs [H-M1] prefix each epoch."""
    ...

def set_seed(seed: int) -> None: ...
```

---

### PermutationProbe (`h-m1/code/probe.py`)

**Dependencies**: FlatMLPEncoder, ExperimentConfig, h-e1/flatten_weights, h-e1/stratified_pair_sample

```python
from typing import Dict, List, Optional, Tuple
import torch
import numpy as np

# Layer order spec: list of (outgoing_weight_key, incoming_weight_key, n_neurons)
LayerOrder = List[Tuple[str, str, int]]

def get_mnist_cnn_layer_order() -> LayerOrder:
    """Return layer permutation spec for Conv(32)-Conv(64)-FC(128)-FC(10)."""
    ...

def generate_permuted_weights(
    state_dict: Dict[str, torch.Tensor],
    layer_order: LayerOrder,
    seed: Optional[int] = None,
) -> Dict[str, torch.Tensor]:
    """Apply random neuron permutation; preserves functional equivalence."""
    ...

def compute_permutation_sensitivity(
    encoder: "FlatMLPEncoder",
    checkpoints: List[Dict],
    mean: torch.Tensor,
    std: torch.Tensor,
    cfg: "ExperimentConfig",
    device: torch.device,
) -> Dict[str, float]:
    """
    Returns: {
        'sensitivity_score': float,
        'mean_equiv_L2': float,
        'mean_random_L2': float,
        'n_pairs': int,
    }
    Uses stratified_pair_sample to get equiv pairs (reuse from h-e1).
    Generates permuted weights via generate_permuted_weights.
    """
    ...
```

---

### Evaluator (`h-m1/code/evaluate.py`)

**Dependencies**: FlatMLPEncoder, WeightDataset, ExperimentConfig

```python
from typing import Dict, Tuple
import torch
from torch.utils.data import DataLoader

def compute_spearman(
    model: "FlatMLPWithHead",
    loader: DataLoader,
    device: torch.device,
) -> float:
    """Compute Spearman ρ on full loader using scipy.stats.spearmanr."""
    ...

def run_gate_check(
    sensitivity_score: float,
    spearman_rho: float,
    param_count: int,
    n_pairs: int,
    cfg: "ExperimentConfig",
) -> Dict[str, object]:
    """
    Returns: {
        'gate_pass': bool,
        'sensitivity_score': float,
        'spearman_rho': float,
        'param_count': int,
        'n_pairs': int,
        'param_in_range': bool,
        'pairs_sufficient': bool,
    }
    Logs [H-M1] gate result.
    """
    ...

def save_results(results: Dict, cfg: "ExperimentConfig") -> None: ...
```

---

### Visualizer (`h-m1/code/visualize.py`)

**Dependencies**: TrainHistory, ExperimentConfig

```python
from typing import Dict, List
import numpy as np

def plot_gate_metrics(
    sensitivity_score: float,
    spearman_rho: float,
    cfg: "ExperimentConfig",
) -> None:
    """Bar chart: sensitivity_score vs 0.3 threshold, Spearman ρ vs 0.5."""
    ...

def plot_l2_distribution(
    equiv_dists: List[float],
    random_dists: List[float],
    cfg: "ExperimentConfig",
) -> None:
    """Histogram: equiv-pair L2 vs random-pair L2 distributions."""
    ...

def plot_training_curve(history: "TrainHistory", cfg: "ExperimentConfig") -> None:
    """Line chart: train/val loss + Spearman ρ over epochs."""
    ...

def plot_sensitivity_by_decile(
    decile_scores: List[float],
    cfg: "ExperimentConfig",
) -> None:
    """Bar chart: sensitivity score per accuracy decile."""
    ...

def plot_embedding_scatter(
    embeddings: np.ndarray,
    accuracies: np.ndarray,
    equiv_pair_indices: List[tuple],
    cfg: "ExperimentConfig",
    method: str = "pca",
) -> None:
    """2D PCA/t-SNE of embeddings; equiv pairs as connected dots."""
    ...
```

---

### RunExperiment (`h-m1/code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """
    Pipeline:
    1. set_seed(42)
    2. load_and_split_dataset → train/val/test + mean/std + all_checkpoints
    3. grid_search_architecture → FlatMLPEncoder + hidden_dims + param_count
    4. train_encoder → trained FlatMLPWithHead + TrainHistory
    5. compute_spearman on test set
    6. compute_permutation_sensitivity → sensitivity results
    7. run_gate_check → gate dict
    8. save_results
    9. generate all 5 figures
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & Project Setup | ExperimentConfig dataclass, directory scaffold, seed utils | 6 | 2+1+1+2 |
| A-2 | Data Loading & Normalization | WeightDataset, Schurholt split extraction, z-score norm, DataLoader builders | 13 | 3+3+4+3 |
| A-3 | FlatMLPEncoder + Grid Search | FlatMLPEncoder, FlatMLPWithHead, grid_search_architecture, count_params | 10 | 3+2+3+2 |
| A-4 | Training Loop | Adam + CosineAnnealingLR, MSE loss, per-epoch Spearman logging, TrainHistory | 12 | 3+3+3+3 |
| A-5 | Permutation Generation | get_mnist_cnn_layer_order, generate_permuted_weights (functional equivalence) | 14 | 3+3+5+3 |
| A-6 | Sensitivity Probing | compute_permutation_sensitivity (equiv vs random L2), h-e1 pair reuse | 15 | 3+4+4+4 |
| A-7 | Evaluation & Gate Check | compute_spearman, run_gate_check, save_results | 9 | 2+2+3+2 |
| A-8 | Visualization (5 figures) | All 5 mandatory figures including t-SNE/PCA scatter with connected pairs | 11 | 2+2+4+3 |
| A-9 | Integration & End-to-End Run | run_experiment.py pipeline, h-e1 sys.path wiring, CUDA setup, smoke test | 12 | 2+3+4+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-6], Medium(9-13): [A-2, A-3, A-4, A-7, A-8, A-9], Low(4-8): [A-1]
