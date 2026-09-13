# Architecture: H-M2
# Permutation Orbit Variance Dominance — Var_perm / (Var_perm + Var_GL) > 0.60

Applied: SVD-based trajectory projection (tomgoldstein/loss-landscape pattern)
Applied: Orbit membership dispatch pattern (h-m1 OrbitPEComputer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 incremental)
**Status**: Patterns found from base code (direct file read — Serena project activation not available)
**Analyzed Path**: `docs/youra_research/20260521_wsl/h-m1/code/`
**Findings**: OrbitPEComputer lives in `orbit_pe_computer.py` (class with `forward(weight, layer_type) -> [cout, token_dim]`). No `get_orbit_basis()` method exists — must wrap. `orbit_pe.py` holds `compute_orbit_pe()`, `_infer_type_from_name()`, `SUPPORTED_LAYER_TYPES`. Data loader is in `data_loader.py` with `SimpleCNN` model matching CNN Zoo architecture.

---

## Module Structure

```
docs/youra_research/20260521_wsl/h-m2/code/
  config.py
  data_loader.py
  orbit_projector.py
  variance_decomposer.py
  evaluate.py
  visualize.py
  run_experiment.py
  figures/          (output directory)
  results/          (output directory)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| OrbitPEComputer | `sys.path.insert(0, h_m1_code_path); from orbit_pe_computer import OrbitPEComputer` | `h-m1/code/orbit_pe_computer.py` |
| compute_orbit_pe_all_layers | `from orbit_pe_computer import compute_orbit_pe_all_layers` | `h-m1/code/orbit_pe_computer.py` |
| _infer_type_from_name | `from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES` | `h-m1/code/orbit_pe.py` |
| _flatten_weight | `from orbit_pe_computer import _flatten_weight` | `h-m1/code/orbit_pe_computer.py` |

**Verified from**: `docs/youra_research/20260521_wsl/h-m1/code/` (actual implementation)

**Critical Note**: `OrbitPEComputer` has `forward(weight, layer_type) -> [cout, token_dim]` and `compute_orbit_id(weight, layer_type) -> [cout]`. It does NOT have `get_orbit_basis()`. The `orbit_projector.py` module must derive the orbit basis from the orbit embeddings matrix.

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from pathlib import Path

H_M1_CODE_PATH: str = "docs/youra_research/20260521_wsl/h-m1/code"

@dataclass
class ExperimentConfig:
    # Paths
    data_dir_cifar10: Path = Path("data/cnn_zoo_cifar10")
    data_dir_svhn: Path = Path("data/cnn_zoo_svhn")
    figures_dir: Path = Path("docs/youra_research/20260521_wsl/h-m2/figures")
    results_dir: Path = Path("docs/youra_research/20260521_wsl/h-m2/results")
    h_m1_code_path: str = H_M1_CODE_PATH
    # Analysis parameters
    min_models: int = 200
    min_checkpoints: int = 10
    max_checkpoints: int = 50
    n_epochs: int = 51
    orbit_basis_dim: int = 64
    token_dim: int = 64
    seed: int = 1
    # Gate
    gate_threshold: float = 0.60
    stability_threshold: float = 0.10
    eps: float = 1e-8

def get_config() -> ExperimentConfig: ...
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: Config

```python
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple
import torch

class TrajectoryDataset:
    def __init__(self, zoo_dir: Path, min_checkpoints: int = 10,
                 max_checkpoints: int = 50): ...
    def discover_models(self) -> List[Path]: ...
    def load_trajectory(self, model_dir: Path) -> List[Dict[str, torch.Tensor]]:
        """Load epoch checkpoints sorted by epoch index. Returns list of state_dicts."""
        ...
    def iter_trajectories(self, n_models: Optional[int] = None
                          ) -> Iterator[Tuple[str, List[Dict[str, torch.Tensor]]]]:
        """Yield (model_id, trajectory) pairs, skipping short trajectories."""
        ...
    def __len__(self) -> int: ...
```

---

### OrbitProjector (`orbit_projector.py`)

**Dependencies**: Config, h-m1/code/orbit_pe_computer.py, h-m1/code/orbit_pe.py

```python
import sys
import torch
import numpy as np
from typing import Dict, Tuple
from torch import Tensor

class OrbitProjector:
    """Wraps h-m1 OrbitPEComputer to provide orbit basis and projection."""
    def __init__(self, token_dim: int = 64, h_m1_code_path: str = "..."): ...

    def get_orbit_basis(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Derive orbit-aligned basis matrix from orbit embeddings.
        Uses OrbitPEComputer.forward() to get per-layer orbit embeddings,
        then stacks and applies SVD to get top-D principal directions.
        Returns: (D, P) where D <= token_dim, P = total flattened param count.
        """
        ...

    def flatten_weights(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Concatenate all weight tensors to 1D vector. Returns: (P,)."""
        ...

    def compute_perm_orbit_projection(self, W_flat: Tensor,
                                       orbit_basis: Tensor) -> Tuple[Tensor, float]:
        """Project W onto permutation orbit subspace.
        orbit_basis: (D, P). Returns: (W_perm, Var_perm scalar)."""
        ...

    def compute_gl_orbit_projection_layer(self, W_layer: Tensor) -> float:
        """GL orbit projection via polar decomposition W = Q*S.
        Returns Var_GL contribution for this layer (scalar)."""
        ...
```

---

### VarianceDecomposer (`variance_decomposer.py`)

**Dependencies**: OrbitProjector, Config

```python
from typing import Dict, List, Tuple
import torch
import numpy as np
from torch import Tensor

class VarianceDecomposer:
    """Decomposes trajectory variance into Var_perm and Var_GL components."""
    def __init__(self, orbit_projector: "OrbitProjector", eps: float = 1e-8): ...

    def compute_trajectory_variance_ratio(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, float]:
        """Compute Var_perm / (Var_perm + Var_GL) for one model trajectory.
        Returns: {ratio, var_perm, var_gl, n_checkpoints}."""
        ...

    def compute_epoch_ratios(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> List[float]:
        """Per-epoch ratio for trajectory evolution plot."""
        ...

    def compute_layer_breakdown(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, Dict[str, float]]:
        """Per-layer (Conv2d vs Linear) Var_perm and Var_GL breakdown."""
        ...

def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict[str, bool]]:
    """Check all mechanism activation indicators. Fail-fast if any False."""
    ...
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: VarianceDecomposer, DataLoader, Config

```python
from typing import Dict, List, Optional
import numpy as np

def run_zoo_analysis(
    dataset: "TrajectoryDataset",
    decomposer: "VarianceDecomposer",
    subset_name: str,
    min_models: int = 200,
) -> Dict:
    """Run variance decomposition on all trajectories. Returns aggregate stats."""
    ...

def compute_cross_dataset_stability(
    ratio_cifar10: float, ratio_svhn: float
) -> Dict[str, float]:
    """Compute |ratio_CIFAR10 - ratio_SVHN| stability gap."""
    ...

def check_gate(results_cifar10: Dict, results_svhn: Dict,
               threshold: float = 0.60, stability_threshold: float = 0.10
               ) -> Dict[str, bool]:
    """Evaluate MUST_WORK gate conditions. Returns pass/fail per criterion."""
    ...

def save_results_json(results: Dict, output_path: str) -> None: ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: evaluate results dict, Config

```python
from pathlib import Path
from typing import Dict, List
import numpy as np

def plot_gate_bar_chart(results_cifar10: Dict, results_svhn: Dict,
                        threshold: float, output_path: Path) -> None:
    """Mandatory gate figure: Var_perm/Var_GL bar chart with 0.60 threshold line."""
    ...

def plot_ratio_histogram(ratios_cifar10: List[float], ratios_svhn: List[float],
                         output_path: Path) -> None: ...

def plot_ratio_vs_epoch(epoch_ratios: List[List[float]], output_path: Path) -> None: ...

def plot_layer_breakdown(layer_stats: Dict, output_path: Path) -> None: ...

def plot_ratio_vs_accuracy(ratios: List[float], accuracies: List[float],
                           output_path: Path) -> None: ...

def save_all_figures(results: Dict, figures_dir: Path) -> None:
    """Generate and save all 5 required figures."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules

```python
def setup_paths(config: "ExperimentConfig") -> None: ...

def run(config: "ExperimentConfig") -> Dict:
    """Full pipeline: data download check → load → decompose → evaluate → visualize → report."""
    ...

def generate_validation_report(results: Dict, output_path: str) -> None:
    """Write 04_validation.md with gate pass/fail and PIVOT recommendation."""
    ...

if __name__ == "__main__":
    # Entry point
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data Preparation | Config, directory setup, wsl-modelzoo install, dataset fetch for CIFAR-10-GS and SVHN-GS | 7 | 1+2+2+2 |
| A-2 | TrajectoryDataset | Implement `data_loader.py`: discover model dirs, load epoch checkpoints, filter short trajectories, iter_trajectories generator | 8 | 2+2+2+2 |
| A-3 | OrbitProjector Wrapper | Implement `orbit_projector.py`: sys.path h-m1 import, derive orbit basis via SVD on orbit embeddings, flatten_weights, perm projection, GL polar decomposition per layer | 14 | 3+4+4+3 |
| A-4 | VarianceDecomposer Core | Implement `variance_decomposer.py`: compute_trajectory_variance_ratio, epoch_ratios, layer_breakdown, verify_mechanism_activated | 13 | 3+4+4+2 |
| A-5 | Evaluate Pipeline | Implement `evaluate.py`: run_zoo_analysis loop over 200+ models, aggregate mean/std, cross-dataset stability, gate check, save JSON | 11 | 2+3+3+3 |
| A-6 | Visualization | Implement `visualize.py`: all 5 figures (gate bar, histogram, epoch evolution, layer breakdown, scatter) | 9 | 2+2+3+2 |
| A-7 | run_experiment.py & Validation Report | Wire full pipeline, generate 04_validation.md with PASS/PIVOT determination | 10 | 2+3+3+2 |
| A-8 | Integration Test & Gate Verification | End-to-end run on subset (20 models), verify mechanism indicators, confirm ratio in valid range | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-5, A-6, A-7], Low(4-8): [A-1, A-2, A-8]

---

## Key Implementation Notes

**get_orbit_basis() does not exist in h-m1**: `OrbitPEComputer` exposes `forward(weight, layer_type) -> [cout, token_dim]` and `compute_orbit_id(weight, layer_type) -> [cout]`. The `OrbitProjector` wrapper must construct an orbit basis by:
1. For each weight param, get orbit embeddings `[cout, token_dim]` via `orbit_computer.forward()`
2. Stack all orbit embedding rows into a matrix `(N_total_channels, token_dim)`
3. Apply SVD; take top-D right singular vectors as the basis in parameter space (requires mapping from embedding space back to weight space via per-channel flattened weight rows)

**Alternative simpler approach**: Use per-layer orbit IDs to construct a binary membership matrix directly from `compute_orbit_id()`, then run SVD on the trajectory drift matrix `∆θ(t) = θ(t) − θ(0)` projected through orbit-aligned columns. This avoids the embedding-space indirection.

**Import pattern for h-m1 modules**:
```python
import sys
sys.path.insert(0, str(Path(config.h_m1_code_path).resolve()))
from orbit_pe_computer import OrbitPEComputer, compute_orbit_pe_all_layers, _flatten_weight
from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES
```
