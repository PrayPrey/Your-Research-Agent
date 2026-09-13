# Architecture: H-E1 — EquiSSL Distribution Shift PoC

**Applied**: Standard DL experiment structure (modular data/model/training/eval layout)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Expected structure: `h-e1/code/` with data, models, training, evaluation subdirectories. External repos (jkalogero/scalegmn, HSG-AIML/MultiZoo-SANE, yiftachbeer/mmd_loss_pytorch) cloned as siblings or installed.

---

## File Organization

```
h-e1/code/
  data/
    multizoo_graph_dataset.py   # MLP/CNN checkpoints → PyG Data objects
    vitzoo_graph_dataset.py     # ViT checkpoints → same graph schema
    augmentations.py            # scale + permutation augmentation for positive pairs
  models/
    equissl_encoder.py          # ScaleGMN wrapper (monomial symmetry)
    graph_decoder.py            # inverse graph decoder (weight reconstruction)
    equissl_objective.py        # NT-Xent + λ*MSE combined loss
  training/
    train_equissl.py            # SSL pre-training loop + λ sweep + checkpointing
    train_sane_baseline.py      # SANE baseline training wrapper
  evaluation/
    mmd_eval.py                 # RBF-MMD computation, ratio + gate check
    visualize.py                # t-SNE, histogram, bar chart figure export
  config.py                     # hardcoded hyperparameters (argparse overrides for λ, seed)
  run_experiment.py             # top-level entry: train both → eval → export results
```

---

## Module Definitions

### MultiZooGraphDataset (`data/multizoo_graph_dataset.py`)

**Dependencies**: torch_geometric, torch

```python
from torch_geometric.data import Dataset, Data
import torch

class MultiZooGraphDataset(Dataset):
    def __init__(self, root: str, zoo_types: list[str] = ['mlp', 'cnn'],
                 split: str = 'train', val_fraction: float = 0.1): ...
    def len(self) -> int: ...
    def get(self, idx: int) -> Data: ...
    # Data schema: x=[n_neurons,1] (bias), edge_attr=[n_edges,d_flat] (weights),
    #              edge_index=[2,n_edges], structure=dict (layer sizes for decoder)

def checkpoint_to_graph(state_dict: dict) -> Data:
    """Convert a PyTorch state_dict to a PyG Data object.
    node_features = bias vectors; edge_features = flattened weight matrices."""
    ...
```

### ViTZooGraphDataset (`data/vitzoo_graph_dataset.py`)

**Dependencies**: torch_geometric, torch

```python
from torch_geometric.data import Dataset, Data

class ViTZooGraphDataset(Dataset):
    def __init__(self, root: str, return_labels: bool = True): ...
    def len(self) -> int: ...
    def get(self, idx: int) -> Data: ...
    # Same graph schema as MultiZooGraphDataset — cross-arch compatibility enforced here
```

### Augmentations (`data/augmentations.py`)

**Dependencies**: torch, torch_geometric

```python
import torch
from torch_geometric.data import Data

def scale_augment(graph: Data, alpha: torch.Tensor | None = None) -> Data:
    """Apply monomial scale aug: scale layer_i by α_i, layer_{i+1} by α_i^{-1}."""
    ...

def perm_augment(graph: Data) -> Data:
    """Randomly permute hidden neuron ordering per layer."""
    ...

def make_positive_pair(graph: Data) -> tuple[Data, Data]:
    """Return two augmented views of the same graph (scale + perm each)."""
    ...
```

### EquiSSLEncoder (`models/equissl_encoder.py`)

**Dependencies**: scalegmn (external), torch, torch_geometric

```python
import torch.nn as nn
from torch_geometric.data import Data

class EquiSSLEncoder(nn.Module):
    def __init__(self, node_in_dim: int = 1, edge_in_dim: int = 1,
                 hidden_dim: int = 256, latent_dim: int = 128,
                 num_layers: int = 4, symmetry: str = 'monomial'): ...
    def forward(self, data: Data) -> torch.Tensor:
        """Returns latent z of shape (B, latent_dim), scale+perm invariant."""
        ...
    # Wraps jkalogero/scalegmn with symmetry='monomial'
    # scalegmn loaded via: sys.path.insert(0, 'path/to/scalegmn'); from scalegmn import ScaleGMN
```

### GraphDecoder (`models/graph_decoder.py`)

**Dependencies**: torch, torch_geometric

```python
import torch.nn as nn

class GraphDecoder(nn.Module):
    def __init__(self, latent_dim: int = 128, hidden_dim: int = 256,
                 max_edge_dim: int = 512): ...
    def forward(self, z: torch.Tensor, structure: dict) -> torch.Tensor:
        """Reconstruct edge_attr (flattened weight matrices) from z and structure."""
        ...
    # Pattern from odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
```

### EquiSSLObjective (`models/equissl_objective.py`)

**Dependencies**: EquiSSLEncoder, GraphDecoder, torch

```python
import torch.nn as nn
import torch.nn.functional as F

def nt_xent_loss(z_a: torch.Tensor, z_b: torch.Tensor,
                 temperature: float = 0.07) -> torch.Tensor: ...

class EquiSSLObjective(nn.Module):
    def __init__(self, encoder: nn.Module, decoder: nn.Module,
                 temperature: float = 0.07, lam: float = 0.1): ...
    def forward(self, graph_a, graph_b) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns (total_loss, z_a). loss = NT-Xent + lam * MSE_recon."""
        ...
```

### Config (`config.py`)

**Dependencies**: none

```python
# All values hardcoded; argparse overrides for --lam, --seed, --data_root

HIDDEN_DIM     = 256
LATENT_DIM     = 128
NUM_LAYERS     = 4
LR             = 1e-3
WEIGHT_DECAY   = 1e-4
BETAS          = (0.9, 0.999)
BATCH_SIZE     = 64
EPOCHS         = 100
T_MAX          = 100
ETA_MIN        = 1e-5
TEMPERATURE    = 0.07
LAMBDA_SWEEP   = [0.01, 0.1, 1.0, 10.0]
SEEDS          = [0, 1, 2, 3, 4]
VAL_FRACTION   = 0.1
N_MMD_KERNELS  = 5
RESULTS_DIR    = 'docs/youra_research/h-e1/'
FIGURES_DIR    = 'docs/youra_research/h-e1/figures/'
```

### TrainEquiSSL (`training/train_equissl.py`)

**Dependencies**: EquiSSLObjective, MultiZooGraphDataset, Augmentations, config

```python
def train_one_epoch(model: nn.Module, loader, optimizer, device) -> dict: ...

def train_equissl(lam: float, seed: int, data_root: str,
                  checkpoint_dir: str) -> str:
    """Train EquiSSL for given λ and seed. Returns path to best checkpoint."""
    ...

def run_lambda_sweep(seed: int, data_root: str) -> dict[float, str]:
    """Train all 4 λ values; return {lam: best_ckpt_path}."""
    ...

def select_best_lambda(sweep_results: dict[float, str],
                       val_loader) -> tuple[float, str]:
    """Pick λ with lowest validation reconstruction loss."""
    ...

if __name__ == '__main__':
    # argparse: --seed, --lam, --data_root, --checkpoint_dir
    ...
```

### TrainSANEBaseline (`training/train_sane_baseline.py`)

**Dependencies**: HSG-AIML/SANE (external), config

```python
def train_sane(seed: int, data_root: str, checkpoint_dir: str) -> str:
    """Wrapper around SANE training. Returns checkpoint path."""
    ...

def extract_sane_latents(checkpoint_path: str, dataset,
                         device: str) -> torch.Tensor:
    """Encode all models in dataset; return z tensor (N, d)."""
    ...

if __name__ == '__main__':
    # argparse: --seed, --data_root, --checkpoint_dir
    ...
```

### MMDEval (`evaluation/mmd_eval.py`)

**Dependencies**: yiftachbeer/mmd_loss_pytorch (external), torch

```python
from mmd_loss import MMDLoss, RBF

def compute_mmd(z_train: torch.Tensor, z_vit: torch.Tensor,
                n_kernels: int = 5) -> float:
    """RBF-MMD with median heuristic bandwidth."""
    ...

def compute_mmd_ratio(sane_train_z, equi_train_z,
                      vit_z) -> dict:
    """Returns {'mmd_sane': float, 'mmd_equi': float, 'ratio': float}."""
    ...

def gate_check(ratio: float) -> str:
    """Returns 'PASS' | 'STOP' | 'WARN' based on ratio thresholds."""
    ...
```

### Visualize (`evaluation/visualize.py`)

**Dependencies**: matplotlib, seaborn, sklearn, torch

```python
def plot_tsne(train_z: torch.Tensor, vit_z: torch.Tensor,
              title: str, save_path: str) -> None: ...

def plot_mmd_comparison(mmd_sane: float, mmd_equi: float,
                        ratio: float, save_path: str) -> None: ...

def plot_distance_histogram(train_z: torch.Tensor, vit_z: torch.Tensor,
                            save_path: str) -> None: ...

def plot_training_curves(curves: dict[float, dict],
                         save_path: str) -> None:
    """curves = {lam: {'ntxent': [...], 'recon': [...]}}"""
    ...
```

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules above

```python
# Entry point: trains both models, encodes all data, computes MMD, exports results

def main(args) -> None:
    # 1. Train SANE baseline (5 seeds)
    # 2. Train EquiSSL λ sweep, select best λ per seed (5 seeds)
    # 3. Encode MultiZoo train + ViT test for both encoders
    # 4. Compute MMD ratio per seed, mean±std
    # 5. Gate check, save results.json, generate figures, write 04_validation.md
    ...

if __name__ == '__main__':
    # argparse: --data_root, --checkpoint_dir, --device
    ...
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E-1 | Graph Data Pipeline | Implement checkpoint-to-graph conversion for MLP/CNN and ViT checkpoints. Shared graph schema (node=bias, edge=weight) must handle variable layer counts/sizes. Augmentation (scale+perm) for positive pairs. | `data/multizoo_graph_dataset.py`, `data/vitzoo_graph_dataset.py`, `data/augmentations.py` | 14/20 | Module_Size=4, Dependencies=3, Algorithm=4, Integration=3 |
| E-2 | EquiSSL Encoder Wrapper | Wrap jkalogero/scalegmn with symmetry='monomial'. Interface must produce (B, latent_dim) invariant embeddings from PyG Data objects. External repo integration is main complexity. | `models/equissl_encoder.py` | 15/20 | Module_Size=3, Dependencies=4, Algorithm=4, Integration=4 |
| E-3 | Graph Decoder + Objective | Implement graph decoder (z → edge_attr) following odyboufalaki autoencoder pattern. Combine with NT-Xent + λ*MSE in EquiSSLObjective. | `models/graph_decoder.py`, `models/equissl_objective.py` | 13/20 | Module_Size=3, Dependencies=3, Algorithm=4, Integration=3 |
| E-4 | SANE Baseline Wrapper | Wrap HSG-AIML/SANE training and latent extraction. Must use same seeds/optimizer as EquiSSL for fair comparison. | `training/train_sane_baseline.py` | 10/20 | Module_Size=2, Dependencies=4, Algorithm=2, Integration=2 |
| E-5 | SSL Training Loop + λ Sweep | Training loop with cosine LR schedule, checkpointing per epoch, λ sweep (4 runs), best-λ selection by val reconstruction loss. | `training/train_equissl.py`, `config.py` | 12/20 | Module_Size=3, Dependencies=3, Algorithm=3, Integration=3 |
| E-6 | MMD Evaluation + Gate Check | Encode all models, compute MMD(train→ViT) for both encoders via yiftachbeer/mmd_loss_pytorch, compute ratio per seed, apply gate logic, save results.json. | `evaluation/mmd_eval.py`, `run_experiment.py` | 11/20 | Module_Size=3, Dependencies=3, Algorithm=3, Integration=2 |
| E-7 | Visualization + Reporting | t-SNE 2D plots, MMD bar chart, distance histogram, training curves for λ sweep. Export all figures + 04_validation.md. | `evaluation/visualize.py`, `run_experiment.py` | 8/20 | Module_Size=2, Dependencies=2, Algorithm=2, Integration=2 |

**Distribution**: High(14-17): [E-1, E-2], Medium(9-13): [E-3, E-4, E-5, E-6], Low(4-8): [E-7]

---

## External Dependencies

| Repo | Purpose | Integration |
|------|---------|-------------|
| jkalogero/scalegmn | EquiSSL encoder backbone | `sys.path` insert or pip install -e |
| HSG-AIML/MultiZoo-SANE | Dataset download scripts + SANE data loader | `sys.path` insert; data downloaded to `./data/multizoo` |
| HSG-AIML/SANE | SANE model + training | `sys.path` insert |
| ModelZoos/ModelZooDownloader | ViT zoo download | run `python download.py --zoo vit` once |
| yiftachbeer/mmd_loss_pytorch | MMD computation | pip install or direct import |
| odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders | Graph decoder pattern reference | reference only (not imported directly) |

---

## Key Technical Decisions

- **Graph schema**: edge_attr flattened to 1D per edge (handles variable weight matrix shapes); `structure` dict carries original shapes for decoder reconstruction — this is the cross-arch compatibility mechanism.
- **ScaleGMN integration**: imported via `sys.path` since it has no pip package; `EquiSSLEncoder.__init__` instantiates internal ScaleGMN with `symmetry='monomial'`.
- **λ selection**: best λ chosen per seed by val reconstruction MSE before MMD eval; avoids λ-tuning on test set.
- **MMD**: `bandwidth=None` in RBF triggers median heuristic automatically per yiftachbeer implementation.
- **Seed parity**: same 5 seeds `[0,1,2,3,4]` used for both SANE and EquiSSL; `torch.manual_seed` + `DataLoader(worker_init_fn=seed_worker)`.
