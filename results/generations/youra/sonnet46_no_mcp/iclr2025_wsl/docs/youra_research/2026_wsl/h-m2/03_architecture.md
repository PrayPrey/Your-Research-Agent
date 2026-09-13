# Architecture: H-M2
# NFN Equivariant Encoder Permutation Sensitivity Probing

Applied: NFN equivariant weight-space pattern (Navon et al. 2023, arXiv:2301.12780)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `h-m1/code/`
**Findings**: `WeightDataset.__getitem__` returns `(flat_w, acc)`; `train_encoder` expects model with `(embedding, prediction)` two-tuple forward; `compute_permutation_sensitivity` uses `_embed_state_dict` which flattens+normalizes internally; `run_gate_check` reads `cfg.sensitivity_gate` scalar. h-m2 must extend `WeightDataset` to also yield structured weight list, and adapt `_embed_state_dict` for NFN forward signature.

---

## File Structure

- `h-m2/code/config.py` — ExperimentConfig extended with NFN fields
- `h-m2/code/models.py` — NPLinear + NFNEncoder + NFNWithHead + grid_search_nfn
- `h-m2/code/data_loader.py` — NFNWeightDataset + load_and_split_dataset_nfn
- `h-m2/code/train.py` — train_encoder (adapted for NFN two-tuple forward)
- `h-m2/code/probe.py` — compute_permutation_sensitivity_nfn (NFN-aware embedding)
- `h-m2/code/evaluate.py` — compute_spearman + run_gate_check_nfn + save_results
- `h-m2/code/visualize.py` — 6 required figures
- `h-m2/code/run_experiment.py` — main entry point

---

## Module Definitions

### ExperimentConfig (`h-m2/code/config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

MNIST_CNN_WEIGHT_SHAPES: List[tuple] = [
    (32, 1, 3, 3),   # conv1.weight
    (32,),            # conv1.bias
    (64, 32, 3, 3),  # conv2.weight
    (64,),            # conv2.bias
    (128, 1024),      # fc1.weight
    (128,),           # fc1.bias
    (10, 128),        # fc2.weight
    (10,),            # fc2.bias
]

@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training (same as h-m1)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # NFN model
    embed_dim: int = 128
    weight_shapes: List[tuple] = field(default_factory=lambda: MNIST_CNN_WEIGHT_SHAPES)
    channel_dim_candidates: List[int] = field(default_factory=lambda: [24, 32, 40, 48, 56])
    n_layers_candidates: List[int] = field(default_factory=lambda: [2, 3, 4])
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    sensitivity_gate_absolute: float = 0.1
    sensitivity_gate_relative: float = 0.3245   # flat_MLP_score(0.6490) * 0.5
    flat_mlp_sensitivity_score: float = 0.6490  # from h-m1
    spearman_target: float = 0.1041             # from h-m1

    def __post_init__(self): ...

@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    figures_dir: Path = Path("./figures")
    def __post_init__(self): ...

def set_seed(seed: int) -> None: ...
```

---

### NPLinear + NFNEncoder + NFNWithHead (`h-m2/code/models.py`)

**Dependencies**: torch

```python
from typing import List, Tuple
import torch
import torch.nn as nn

class NPLinear(nn.Module):
    """Permutation-equivariant linear layer (Navon et al. 2023).
    Maps list of per-layer tensors (B, n_out_i, in_ch) → list (B, n_out_i, out_ch).
    Uses diag (per-neuron) + bias_terms (pooled invariant) to preserve equivariance.
    """
    def __init__(self, in_ch: int, out_ch: int, weight_shapes: List[tuple]): ...
    def forward(self, Ws: List[torch.Tensor]) -> List[torch.Tensor]: ...
    # Each Ws[i]: (B, n_elements_i, in_ch)
    # Returns: list of (B, n_elements_i, out_ch)


class NFNEncoder(nn.Module):
    """NFN equivariant encoder: structured weight list → (B, embed_dim) embedding.
    in_proj: NPLinear(1, channel_dim) + n_layers-1 NPLinear(channel_dim, channel_dim)
    readout: Linear(channel_dim, embed_dim) after global mean pool.
    """
    def __init__(
        self,
        weight_shapes: List[tuple],
        channel_dim: int,
        embed_dim: int = 128,
        n_layers: int = 3,
    ): ...
    def forward(self, weights: List[torch.Tensor]) -> torch.Tensor:
        # weights: list of 8 tensors, each (B, ...)
        # Returns: (B, embed_dim)
        ...


class NFNWithHead(nn.Module):
    """NFN encoder + Linear(embed_dim, 1) prediction head."""
    def __init__(self, encoder: NFNEncoder, embed_dim: int = 128): ...
    def forward(self, weights: List[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        # Returns: (embedding (B, embed_dim), prediction (B, 1))
        ...


def count_params(model: nn.Module) -> int: ...

def grid_search_nfn(
    weight_shapes: List[tuple],
    channel_dim_candidates: List[int],
    n_layers_candidates: List[int],
    embed_dim: int,
    target_min: int,
    target_max: int,
) -> Tuple[NFNEncoder, int, int, int]:
    # Returns: (encoder, channel_dim, n_layers, param_count)
    # Iterates channel_dim × n_layers grid; returns first within [target_min, target_max]
    ...
```

---

### NFNWeightDataset (`h-m2/code/data_loader.py`)

**Dependencies**: torch, h-m1/code/data_loader.py (_load_raw_splits, build_dataloaders)

```python
from typing import Dict, List, Optional, Tuple
import torch
from torch.utils.data import Dataset, DataLoader

# Reused from h-m1 (import directly):
# from sys import path; path.insert(0, "h-m1/code")
# from data_loader import _load_raw_splits, build_dataloaders

WEIGHT_KEY_ORDER: List[str] = [
    "module_list.0.weight", "module_list.0.bias",
    "module_list.3.weight", "module_list.3.bias",
    "module_list.6.weight", "module_list.6.bias",
    "module_list.9.weight", "module_list.9.bias",
]
# Note: actual keys verified at runtime from first checkpoint state_dict


class NFNWeightDataset(Dataset):
    """Yields (weight_list, flat_w_normalized, acc) per checkpoint.

    weight_list: List[Tensor] — 8 per-layer tensors for NFN forward
    flat_w_normalized: Tensor (input_dim,) — for permutation generation compatibility
    acc: scalar Tensor
    """
    def __init__(
        self,
        checkpoints: List[Dict],
        mean: Optional[torch.Tensor] = None,
        std: Optional[torch.Tensor] = None,
    ): ...

    def _extract_weight_list(self, state_dict) -> List[torch.Tensor]:
        # Returns ordered list of 8 tensors (float32, cpu)
        # Key order: conv1.w, conv1.b, conv2.w, conv2.b, fc1.w, fc1.b, fc2.w, fc2.b
        ...

    def _flatten(self, state_dict) -> torch.Tensor: ...  # same as h-m1

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> Tuple[List[torch.Tensor], torch.Tensor, torch.Tensor]:
        # Returns: (weight_list, flat_w_normalized, acc)
        ...


def load_and_split_dataset_nfn(cfg) -> Tuple[
    "NFNWeightDataset", "NFNWeightDataset", "NFNWeightDataset",
    torch.Tensor, torch.Tensor,
    List[Dict],
]:
    # Loads zoo, computes z-score stats from train set, returns NFNWeightDataset splits
    # Reuses _load_raw_splits from h-m1
    ...


def collate_nfn(batch):
    # Custom collate: stack weight_list per-layer across batch
    # Returns: (List[Tensor(B,...)], Tensor(B,input_dim), Tensor(B,))
    ...


def build_dataloaders_nfn(
    train_ds: "NFNWeightDataset",
    val_ds: "NFNWeightDataset",
    test_ds: "NFNWeightDataset",
    cfg,
) -> Tuple[DataLoader, DataLoader, DataLoader]: ...
```

---

### train_encoder (`h-m2/code/train.py`)

**Dependencies**: models.NFNWithHead, torch

```python
from dataclasses import dataclass, field
from typing import Tuple
import torch
from torch.utils.data import DataLoader

@dataclass
class TrainHistory:
    train_loss: list = field(default_factory=list)
    val_loss: list = field(default_factory=list)
    train_spearman: list = field(default_factory=list)
    val_spearman: list = field(default_factory=list)


def train_encoder(
    model,           # NFNWithHead — forward(weight_list) → (embedding, pred)
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg,
    device: torch.device,
) -> Tuple[object, TrainHistory]:
    # Adam + CosineAnnealingLR + MSELoss; same as h-m1 but unpacks (weight_list, flat_w, acc)
    # batch from loader: (weight_list_batched, flat_w, acc) — uses weight_list_batched for forward
    # Saves best-val-loss checkpoint; logs every epoch
    ...
```

---

### compute_permutation_sensitivity_nfn (`h-m2/code/probe.py`)

**Dependencies**: h-m1/code/probe.py (generate_permuted_weights, get_mnist_cnn_layer_order), models.NFNEncoder, data_loader.NFNWeightDataset

```python
from typing import Dict, List, Tuple
import torch

# Direct reuse (via sys.path insert to h-m1/code):
# from probe import generate_permuted_weights, get_mnist_cnn_layer_order

def _embed_nfn(
    encoder,              # NFNEncoder in eval mode
    state_dict: Dict,
    weight_key_order: List[str],
    device: torch.device,
) -> torch.Tensor:
    # Extracts ordered weight list from state_dict → forward through NFNEncoder
    # Returns: (embed_dim,) on CPU
    ...


def compute_permutation_sensitivity_nfn(
    encoder,              # NFNEncoder
    checkpoints: List[Dict],
    weight_key_order: List[str],
    cfg,
    device: torch.device,
) -> Dict:
    # Reuses stratified_pair_sample from h-e1/code/weight_analysis.py (same as h-m1)
    # Reuses generate_permuted_weights from h-m1/code/probe.py
    # Computes: sensitivity_score = mean_equiv_L2 / mean_random_L2
    # Returns: {sensitivity_score, mean_equiv_L2, mean_random_L2, n_pairs,
    #           equiv_dists, random_dists, decile_scores}
    ...
```

---

### evaluate (`h-m2/code/evaluate.py`)

**Dependencies**: torch, scipy, models.NFNWithHead

```python
from typing import Dict
import torch
from torch.utils.data import DataLoader

def compute_spearman(
    model,          # NFNWithHead — forward(weight_list) → (embedding, pred)
    loader: DataLoader,
    device: torch.device,
) -> float:
    # Unpacks (weight_list, flat_w, acc) from loader
    # Returns Spearman rho (float)
    ...


def run_gate_check_nfn(
    sensitivity_score: float,
    spearman_rho: float,
    param_count: int,
    n_pairs: int,
    cfg,
) -> Dict:
    # gate_absolute = sensitivity_score < cfg.sensitivity_gate_absolute (0.1)
    # gate_relative = sensitivity_score < cfg.sensitivity_gate_relative (0.3245)
    # gate_pass = gate_absolute AND gate_relative
    # Returns full metrics dict
    ...


def save_results(results: Dict, cfg) -> None:
    # Saves to cfg.results_dir / "h-m2_results.json"
    ...
```

---

### visualize (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, numpy, sklearn.decomposition.PCA

```python
from typing import Dict, List
import numpy as np

def plot_gate_metrics_comparison(
    nfn_score: float,
    flat_mlp_score: float,
    threshold_abs: float,
    threshold_rel: float,
    figures_dir,
) -> None:
    # FR-7.1: bar chart NFN score vs thresholds vs flat MLP
    ...

def plot_l2_distribution_comparison(
    nfn_equiv_dists: List[float],
    nfn_random_dists: List[float],
    mlp_equiv_dists: List[float],
    mlp_random_dists: List[float],
    figures_dir,
) -> None:
    # FR-7.2: side-by-side histograms
    ...

def plot_embedding_pca(
    embeddings: np.ndarray,       # (N, embed_dim)
    accuracies: np.ndarray,       # (N,)
    equiv_pair_indices: List[tuple],
    figures_dir,
) -> None:
    # FR-7.3: PCA scatter with connected equiv pairs
    ...

def plot_training_curves(
    history,   # TrainHistory
    figures_dir,
) -> None:
    # FR-7.4: loss + Spearman rho over epochs
    ...

def plot_sensitivity_by_decile(
    nfn_decile_scores: List[float],
    mlp_decile_scores: List[float],
    figures_dir,
) -> None:
    # FR-7.5: NFN per-decile bar chart
    ...

def plot_nfn_vs_mlp_decile_comparison(
    nfn_decile_scores: List[float],
    mlp_decile_scores: List[float],
    figures_dir,
) -> None:
    # FR-7.6: grouped bar NFN vs flat MLP per decile
    ...
```

---

### run_experiment (`h-m2/code/run_experiment.py`)

**Dependencies**: all h-m2 modules

```python
def main() -> None:
    # 1. set_seed(42)
    # 2. load_and_split_dataset_nfn(cfg) → splits, mean, std, all_checkpoints
    # 3. grid_search_nfn(...) → nfn_encoder, channel_dim, n_layers, param_count
    # 4. NFNWithHead(nfn_encoder) → nfn_model
    # 5. build_dataloaders_nfn(...) → train/val/test loaders
    # 6. train_encoder(nfn_model, ...) → trained_model, history
    # 7. compute_spearman(trained_model, test_loader, device)
    # 8. compute_permutation_sensitivity_nfn(nfn_encoder, all_checkpoints, ...) → probe_results
    # 9. run_gate_check_nfn(...) → gate_results
    # 10. save_results(...)
    # 11. Generate all 6 figures via visualize.*
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

**Verified from**: `h-m1/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| `_load_raw_splits` | `sys.path.insert(0, "h-m1/code"); from data_loader import _load_raw_splits` | `h-m1/code/data_loader.py` |
| `build_dataloaders` | `from data_loader import build_dataloaders` | `h-m1/code/data_loader.py` |
| `train_encoder` (signature only) | Reimplemented in h-m2/code/train.py — NFN collate differs | N/A |
| `generate_permuted_weights` | `sys.path.insert(0, "h-m1/code"); from probe import generate_permuted_weights` | `h-m1/code/probe.py` |
| `get_mnist_cnn_layer_order` | `from probe import get_mnist_cnn_layer_order` | `h-m1/code/probe.py` |
| `stratified_pair_sample` | `sys.path.insert(0, "h-e1/code"); from weight_analysis import stratified_pair_sample` | `h-e1/code/weight_analysis.py` |

**Key implementation notes from actual h-m1 code:**
- `_embed_state_dict` in h-m1/probe.py flattens state_dict internally — h-m2 needs `_embed_nfn` that extracts ordered weight list instead
- `train_encoder` in h-m1 expects `(x, y)` batches with flat tensor `x`; h-m2 must adapt loop for `(weight_list, flat_w, acc)` collated batches
- `run_gate_check` in h-m1 uses single `cfg.sensitivity_gate` scalar; h-m2 uses dual thresholds `sensitivity_gate_absolute` + `sensitivity_gate_relative`
- `get_mnist_cnn_layer_order` returns actual hyp_rand keys `module_list.{0,3,6,9,11}` with architecture Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10) — NOT the canonical Conv(32)-Conv(64)-FC(128)-FC(10) described in PRD; `_extract_weight_list` must discover actual keys at runtime from first checkpoint

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, config.py with NFN fields, MNIST_CNN_WEIGHT_SHAPES constant, set_seed | 5 | 1+1+1+2 |
| A-2 | NFNWeightDataset | Extend h-m1 WeightDataset: structured weight list extraction, collate_nfn, load_and_split_dataset_nfn | 10 | 2+3+3+2 |
| A-3 | NPLinear Layer | Permutation-equivariant linear layer: diag + bias_terms path, correct tensor reshape for conv/bias shapes | 14 | 3+2+5+4 |
| A-4 | NFNEncoder + NFNWithHead | Stack NPLinear layers, global mean pool readout, two-tuple forward, grid_search_nfn | 13 | 3+3+4+3 |
| A-5 | Train Loop Adaptation | Adapt train_encoder for NFN collated batches, same optimizer/scheduler/loss as h-m1 | 9 | 2+3+2+2 |
| A-6 | NFN Probing | _embed_nfn using structured weight list; compute_permutation_sensitivity_nfn reusing stratified_pair_sample + generate_permuted_weights | 12 | 2+4+4+2 |
| A-7 | Evaluation + Gate Check | compute_spearman for NFN loader format; run_gate_check_nfn dual thresholds; save_results | 8 | 2+2+2+2 |
| A-8 | 6 Required Figures | plot_gate_metrics_comparison, L2 histograms, PCA scatter, training curves, decile bars, grouped comparison | 10 | 2+2+3+3 |
| A-9 | run_experiment.py | Wire all modules; verify param_count in range pre-training; gate logging; results + figures | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-5, A-6, A-8, A-9], Low(4-8): [A-1, A-7]
