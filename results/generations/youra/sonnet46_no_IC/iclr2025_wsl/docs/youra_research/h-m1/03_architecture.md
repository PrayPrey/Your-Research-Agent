# Architecture: H-M1
# Graph Representation as Cross-Architecture Generalization Mechanism

Applied: standard-DL-experiment-pipeline (no relevant Archon KB patterns found for weight-space domain)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 incremental extension)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has `MultiZooGraphDataset`, `ViTZooGraphDataset`, `EquiSSLEncoder`, `EquiSSLObjective`, `MMDLoss`, and training/eval functions. H-M1 extends by adding EquiSSL-perm training + linear probe evaluation replacing MMD evaluation.

---

## External Dependencies

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MultiZooGraphDataset | `from he1.data.multizoo_graph_dataset import MultiZooGraphDataset` | `h-e1/code/data/multizoo_graph_dataset.py` |
| ViTZooGraphDataset | `from he1.data.vitzoo_graph_dataset import ViTZooGraphDataset` | `h-e1/code/data/vitzoo_graph_dataset.py` |
| checkpoint_to_graph | `from he1.data.multizoo_graph_dataset import checkpoint_to_graph` | `h-e1/code/data/multizoo_graph_dataset.py` |
| EquiSSLEncoder | `from he1.models.equissl_encoder import EquiSSLEncoder` | `h-e1/code/models/equissl_encoder.py` |
| EquiSSLObjective | `from he1.models.equissl_objective import EquiSSLObjective` | `h-e1/code/models/equissl_objective.py` |
| load_encoder_from_checkpoint | `from he1.training.train_equissl import load_encoder_from_checkpoint` | `h-e1/code/training/train_equissl.py` |
| Augmentations | `from he1.data.augmentations import PermutationAugment, ScaleAugment` | `h-e1/code/data/augmentations.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: H-E1 `ViTZooGraphDataset` handles synthetic ViT-like zoo. H-M1 must extend it for real ViT Model Zoo (250 real checkpoints with accuracy labels). `create_synthetic_vit_zoo` is replaced by a real downloader path.

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class EquiSSLPermConfig:
    symmetry: str = "permutation"
    node_dim: int = 64
    edge_dim: int = 64
    hidden_dim: int = 256
    latent_dim: int = 128
    num_layers: int = 4
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 64
    epochs: int = 100
    temperature: float = 0.07
    lambda_rec: float = 0.1
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    t_max: int = 100
    eta_min: float = 1e-5

@dataclass
class LinearProbeConfig:
    alphas: List[float] = field(default_factory=lambda: [0.1, 1.0, 10.0, 100.0])
    test_size: float = 0.2
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

@dataclass
class PathConfig:
    he1_checkpoint_dir: str = "docs/youra_research/h-e1/checkpoints"
    checkpoint_dir: str = "docs/youra_research/h-m1/checkpoints"
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    vit_zoo_root: str = "data/vitzoo"
    multizoo_root: str = "data/multizoo"

@dataclass
class ExperimentConfig:
    equi_perm: EquiSSLPermConfig = field(default_factory=EquiSSLPermConfig)
    probe: LinearProbeConfig = field(default_factory=LinearProbeConfig)
    paths: PathConfig = field(default_factory=PathConfig)
```

---

### RealViTZooDataset (`code/data/real_vit_zoo_dataset.py`)

**Dependencies**: `he1.data.vitzoo_graph_dataset.ViTZooGraphDataset`, `checkpoint_to_graph`

```python
import torch
from torch.utils.data import Dataset
from torch_geometric.data import Data

class RealViTZooDataset(Dataset):
    """250 real ViT checkpoints with accuracy labels → graph representation."""

    def __init__(self, root: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Data, float]: ...
    def get_accuracy_labels(self) -> torch.Tensor: ...
    def get_all_graphs(self) -> list[Data]: ...

def vit_checkpoint_to_graph(state_dict: dict) -> Data:
    """Convert ViT state_dict → computational graph per GMN paper (ICLR 2024).
    Multi-head attention: Q/K/V → parameter subgraph, head_id as node feature.
    Feedforward: MLP subgraph (node=neuron, edge=weight).
    LayerNorm: scale/bias as node features.
    """
    ...
```

---

### EquiSSLPermEncoder (`code/models/equi_perm_encoder.py`)

**Dependencies**: `he1.models.equissl_encoder.EquiSSLEncoder`, `he1.models.equissl_objective.EquiSSLObjective`

```python
import torch.nn as nn
from torch_geometric.data import Batch

class EquiSSLPermEncoder(nn.Module):
    """ScaleGMN with symmetry=permutation (permutation-only equivariance).
    Wraps ScaleGMN backbone; identical architecture to EquiSSL except symmetry flag.
    """

    def __init__(self, cfg: EquiSSLPermConfig): ...
    def forward(self, batch: Batch) -> torch.Tensor: ...
    def encode(self, batch: Batch) -> torch.Tensor: ...
```

---

### EquiSSLPermTrainer (`code/training/train_equi_perm.py`)

**Dependencies**: `EquiSSLPermEncoder`, `EquiSSLObjective` (from H-E1), `MultiZooGraphDataset` (H-E1), `augmentations` (H-E1 permutation-only)

```python
def train_equi_perm(cfg: EquiSSLPermConfig, seed: int, path_cfg: PathConfig) -> str:
    """Train EquiSSL-perm for one seed. Returns checkpoint path.
    Uses NT-Xent + lambda*MSE. Permutation augmentation only (no scale).
    """
    ...

def train_all_seeds(cfg: ExperimentConfig) -> list[str]:
    """Train EquiSSL-perm for all 5 seeds. Returns list of checkpoint paths."""
    ...
```

---

### EmbeddingExtractor (`code/evaluation/extract_embeddings.py`)

**Dependencies**: `RealViTZooDataset`, `EquiSSLPermEncoder`, `he1.training.train_equissl.load_encoder_from_checkpoint`, SANE (H-E1)

```python
import numpy as np

def extract_graph_embeddings(
    encoder: nn.Module,
    vit_dataset: RealViTZooDataset,
    device: str = "cuda",
) -> np.ndarray:
    """Frozen encoder → embeddings for all 250 ViT models. Shape: (250, latent_dim)."""
    ...

def extract_sane_embeddings(
    checkpoint_path: str,
    vit_zoo_root: str,
    chunk_size: int = 512,
    device: str = "cuda",
) -> np.ndarray:
    """Load frozen SANE → flat chunk embeddings for 250 ViT models."""
    ...

def extract_all_embeddings(cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """Extract embeddings for SANE, EquiSSL, EquiSSL-perm × 5 seeds.
    Returns dict keyed by f'{model_name}_seed{i}', shape (250, latent_dim).
    """
    ...
```

---

### LinearProbeEvaluator (`code/evaluation/linear_probe.py`)

**Dependencies**: `sklearn`, `scipy`

```python
import numpy as np
from dataclasses import dataclass

@dataclass
class ProbeResult:
    r2_per_seed: list[float]
    r2_mean: float
    r2_std: float

@dataclass
class StatTestResult:
    t_stat: float
    p_value: float
    significant: bool  # p < 0.05

def evaluate_linear_probe(
    embeddings: np.ndarray,  # (250, latent_dim)
    labels: np.ndarray,      # (250,)
    cfg: LinearProbeConfig,
) -> ProbeResult:
    """RidgeCV on frozen embeddings → R² per seed over 5 80/20 splits."""
    ...

def paired_ttest(
    r2_graph: list[float],
    r2_sane: list[float],
) -> StatTestResult:
    """scipy.stats.ttest_rel over 5 seed R² values."""
    ...

def evaluate_all_models(
    embeddings_dict: dict[str, np.ndarray],
    labels: np.ndarray,
    cfg: LinearProbeConfig,
) -> dict[str, ProbeResult]:
    """Run linear probe for SANE, EquiSSL-perm, EquiSSL × 5 seeds.
    Aggregates per-seed R² across seeds.
    """
    ...

def run_significance_tests(
    results: dict[str, ProbeResult],
) -> dict[str, StatTestResult]:
    """Paired t-tests: EquiSSL-perm vs SANE, EquiSSL vs SANE."""
    ...

def evaluate_gate(stat_tests: dict[str, StatTestResult]) -> str:
    """Returns 'PASS', 'PARTIAL', or 'FAIL' based on p < 0.05 for both graph encoders."""
    ...
```

---

### FigureGenerator (`code/evaluation/figures.py`)

**Dependencies**: `matplotlib`, `seaborn`, `sklearn.manifold.TSNE`, `LinearProbeEvaluator` results

```python
def plot_r2_bar_chart(
    results: dict[str, ProbeResult],
    stat_tests: dict[str, StatTestResult],
    save_path: str,
) -> None:
    """Figure 1: Bar chart R²(SANE) vs R²(EquiSSL-perm) vs R²(EquiSSL) with
    error bars (std), threshold line at SANE R², p-value annotations.
    """
    ...

def plot_ablation_ladder(
    results: dict[str, ProbeResult],
    save_path: str,
) -> None:
    """Figure 2: Grouped bar chart — 3 methods × ViT accuracy prediction R²."""
    ...

def plot_tsne_comparison(
    embeddings_dict: dict[str, np.ndarray],
    arch_labels: list[str],
    save_path: str,
) -> None:
    """Figure 3: 4-panel t-SNE — SANE / EquiSSL-perm / EquiSSL latent spaces,
    colored by architecture family.
    """
    ...

def plot_paired_seed_scatter(
    results: dict[str, ProbeResult],
    save_path: str,
) -> None:
    """Figure 4: Per-seed R² scatter (graph vs SANE); dots above diagonal = improvement."""
    ...

def plot_vit_accuracy_distribution(
    labels: np.ndarray,
    save_path: str,
) -> None:
    """Figure 5: Histogram of 250 ViT model accuracies."""
    ...

def generate_all_figures(
    results: dict[str, ProbeResult],
    stat_tests: dict[str, StatTestResult],
    embeddings_dict: dict[str, np.ndarray],
    labels: np.ndarray,
    figures_dir: str,
) -> None: ...
```

---

### ReportWriter (`code/evaluation/report.py`)

**Dependencies**: `LinearProbeEvaluator` results

```python
def write_validation_report(
    results: dict[str, ProbeResult],
    stat_tests: dict[str, StatTestResult],
    gate_outcome: str,
    output_path: str,
) -> None:
    """Write docs/youra_research/h-m1/04_validation.md.
    Includes R² table, t-stat/p-value, gate evaluation, figure references.
    """
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: All modules above

```python
def get_parser() -> argparse.ArgumentParser: ...

def main() -> None:
    """Orchestrates full H-M1 pipeline:
    1. Train EquiSSL-perm (5 seeds)
    2. Extract embeddings (SANE + EquiSSL from H-E1, EquiSSL-perm new)
    3. Run linear probe evaluation
    4. Statistical significance tests + gate check
    5. Generate 5 figures
    6. Write 04_validation.md
    """
    ...
```

---

## File Organization

```
code/
├── config.py
├── run_experiment.py
├── data/
│   └── real_vit_zoo_dataset.py
├── models/
│   └── equi_perm_encoder.py
├── training/
│   └── train_equi_perm.py
└── evaluation/
    ├── extract_embeddings.py
    ├── linear_probe.py
    ├── figures.py
    └── report.py
```

Reused from H-E1 (no copy, direct import):
- `h-e1/code/data/multizoo_graph_dataset.py` — MultiZooGraphDataset, checkpoint_to_graph
- `h-e1/code/data/augmentations.py` — PermutationAugment
- `h-e1/code/models/equissl_encoder.py` — EquiSSLEncoder (for EquiSSL embedding extraction)
- `h-e1/code/models/equissl_objective.py` — EquiSSLObjective (NT-Xent + MSE)
- `h-e1/code/training/train_equissl.py` — load_encoder_from_checkpoint

Checkpoints reused (read-only):
- `h-e1/checkpoints/sane_seed{0..4}.pt`
- `h-e1/checkpoints/equi_seed{0..4}.pt`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config dataclasses, path setup, H-E1 import validation | 6 | 1+1+2+2 |
| A-2 | Real ViT Zoo Dataset | `RealViTZooDataset` + `vit_checkpoint_to_graph` (attention subgraph per GMN paper, Q/K/V, LayerNorm node features) | 16 | 4+3+5+4 |
| A-3 | EquiSSL-perm Encoder | `EquiSSLPermEncoder` wrapping ScaleGMN with `symmetry=permutation` flag, verify forward pass and graph batch compatibility | 14 | 3+4+4+3 |
| A-4 | EquiSSL-perm Training | `train_equi_perm` for 5 seeds, permutation-only augmentation, NT-Xent + λMSE, CosineAnnealingLR, checkpoint saving | 15 | 3+4+4+4 |
| A-5 | Embedding Extraction | `extract_all_embeddings` for SANE + EquiSSL (H-E1 frozen) + EquiSSL-perm (new) × 5 seeds × 250 ViT models | 13 | 3+4+3+3 |
| A-6 | Linear Probe Evaluation | `evaluate_all_models` (RidgeCV 80/20 per seed), `run_significance_tests` (paired t-test), `evaluate_gate` (PASS/PARTIAL/FAIL) | 10 | 2+2+3+3 |
| A-7 | Figure Generation | All 5 figures: bar chart, ablation ladder, t-SNE 4-panel, paired scatter, ViT accuracy histogram | 12 | 3+2+4+3 |
| A-8 | Report & Orchestration | `write_validation_report` (04_validation.md), `run_experiment.py` full pipeline wiring, end-to-end test | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3, A-4], Medium(9-13): [A-5, A-6, A-7, A-8], Low(4-8): [A-1]

**Total Complexity**: 95
**Task Count**: 8 (within MECHANISM 6-12 range)
