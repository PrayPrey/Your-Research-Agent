# Logic: H-M2
# Permutation Orbit Variance Dominance — Var_perm / (Var_perm + Var_GL) > 0.60

Applied: PyTorch nn.Module API pattern
Applied: SVD-based trajectory projection (tomgoldstein/loss-landscape)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 incremental)
**Status**: API signatures verified from actual h-m1 code (direct file read; Serena project activation unavailable for this path)
**Analyzed Path**: `docs/youra_research/20260521_wsl/h-m1/code/`
**Relevant Symbols**:
- `OrbitPEComputer.__init__(token_dim: int, orbit_embed_dim: int = 64)`
- `OrbitPEComputer.forward(weight: Tensor, layer_type: str) -> Tensor`  # [cout, token_dim]
- `OrbitPEComputer.compute_orbit_id(weight: Tensor, layer_type: str) -> Tensor`  # [cout] int64
- `compute_orbit_pe_all_layers(state_dict, orbit_computer, n_heads=1) -> Tuple[Dict, Dict]`
- `_flatten_weight(weight: Tensor, layer_type: str, n_heads: int = 1) -> Tensor`  # [cout, cin_flat]
- `_infer_type_from_name(param_name: str, weight: Tensor) -> str`
- `SUPPORTED_LAYER_TYPES = ["Linear", "Conv2d", "MultiheadAttention"]`

**Critical Finding**: `OrbitPEComputer` has NO `get_orbit_basis()` method. The `orbit_embedding` table maps orbit IDs to `[cout, token_dim]` embeddings — not a parameter-space basis. `OrbitProjector` must construct orbit basis from orbit membership via SVD on trajectory delta matrix (see A-3 pseudo-code).

---

## External Dependencies API

### Verified from `docs/youra_research/20260521_wsl/h-m1/code/orbit_pe_computer.py`

```python
class OrbitPEComputer(nn.Module):
    def __init__(self, token_dim: int, orbit_embed_dim: int = 64): ...
    # orbit_embed_dim is internally overridden to token_dim

    def compute_orbit_id(self, weight: Tensor, layer_type: str) -> Tensor:
        # weight: [cout, cin] | [cout, cin, kH, kW]
        # returns: [cout] int64 (row-norm rank, 0-indexed)
        ...

    def forward(self, weight: Tensor, layer_type: str) -> Tensor:
        # weight: [cout, cin] | [cout, cin, kH, kW]
        # returns: [cout, token_dim]
        ...

def compute_orbit_pe_all_layers(
    state_dict: Dict[str, Tensor],
    orbit_computer: OrbitPEComputer,
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    # returns: orbit_vecs {param_name -> [cout, token_dim]}, success_flags
    ...

def _flatten_weight(weight: Tensor, layer_type: str, n_heads: int = 1) -> Tensor:
    # Conv2d [cout,cin,kH,kW] -> [cout, cin*kH*kW]
    # Linear [cout,cin] -> [cout, cin]  (unchanged)
    ...
```

**Verified from**: `docs/youra_research/20260521_wsl/h-m1/code/orbit_pe_computer.py` (actual code)

**Import pattern**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(config.h_m1_code_path).resolve()))
from orbit_pe_computer import OrbitPEComputer, compute_orbit_pe_all_layers, _flatten_weight
from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES
```

---

## A-1: Setup & Data Preparation [Complexity: 7, Budget: 1]

**Applied**: Standard dataclass config pattern

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from pathlib import Path

H_M1_CODE_PATH: str = "docs/youra_research/20260521_wsl/h-m1/code"

@dataclass
class ExperimentConfig:
    data_dir_cifar10: Path = Path("data/cnn_zoo_cifar10")
    data_dir_svhn: Path = Path("data/cnn_zoo_svhn")
    figures_dir: Path = Path("docs/youra_research/20260521_wsl/h-m2/figures")
    results_dir: Path = Path("docs/youra_research/20260521_wsl/h-m2/results")
    h_m1_code_path: str = H_M1_CODE_PATH
    min_models: int = 200
    min_checkpoints: int = 10
    max_checkpoints: int = 50
    n_epochs: int = 51
    orbit_basis_dim: int = 64
    token_dim: int = 64
    seed: int = 1
    gate_threshold: float = 0.60
    stability_threshold: float = 0.10
    eps: float = 1e-8

def get_config() -> ExperimentConfig: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config_and_dirs | Implement ExperimentConfig, get_config(), mkdir for figures/results dirs |

---

## A-2: TrajectoryDataset [Complexity: 8, Budget: 1]

**Applied**: Standard PyTorch

### API Signatures

```python
# data_loader.py
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple
import torch

class TrajectoryDataset:
    def __init__(self, zoo_dir: Path, min_checkpoints: int = 10,
                 max_checkpoints: int = 50): ...

    def discover_models(self) -> List[Path]:
        """Return sorted list of model dirs with >= min_checkpoints epoch_*.pt files."""
        ...

    def load_trajectory(self, model_dir: Path) -> List[Dict[str, torch.Tensor]]:
        """Load epoch checkpoints sorted by epoch index. Returns list of state_dicts."""
        # epoch_*.pt files, sorted, up to max_checkpoints
        ...

    def iter_trajectories(
        self, n_models: Optional[int] = None
    ) -> Iterator[Tuple[str, List[Dict[str, torch.Tensor]]]]:
        """Yield (model_id, trajectory) pairs, skipping short trajectories."""
        ...

    def __len__(self) -> int: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | trajectory_dataset | Implement TrajectoryDataset with discover, load, iter |

---

## A-3: OrbitProjector Wrapper [Complexity: 14, Budget: 2]

**Applied**: SVD-based trajectory projection (tomgoldstein/loss-landscape)

### API Signatures

```python
# orbit_projector.py
import sys, torch, numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from torch import Tensor
from scipy.linalg import polar

class OrbitProjector:
    """Wraps h-m1 OrbitPEComputer to derive orbit basis and project trajectories."""

    def __init__(self, token_dim: int = 64, h_m1_code_path: str = "..."): ...
    # Initializes self.orbit_computer = OrbitPEComputer(token_dim=token_dim)

    def flatten_weights(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Concatenate all .weight tensors (supported layers) to 1D.
        state_dict: epoch state_dict
        returns: [P] float32
        """
        ...

    def get_orbit_basis(self, state_dict: Dict[str, Tensor]) -> Tensor:
        """Derive orbit-aligned basis in parameter space via SVD on orbit ID matrix.
        state_dict: single epoch (reference checkpoint, typically epoch 0)
        returns: [D, P]  D <= orbit_basis_dim, P = total param count
        """
        ...

    def compute_perm_orbit_projection(
        self, W_flat: Tensor, orbit_basis: Tensor
    ) -> Tuple[Tensor, float]:
        """Project W onto permutation orbit subspace.
        W_flat: [P]
        orbit_basis: [D, P]
        returns: (W_perm [P], var_perm scalar)
        """
        ...

    def compute_gl_orbit_projection_layer(
        self, W_layer: Tensor, layer_type: str
    ) -> float:
        """GL orbit projection via polar decomposition W = Q*S.
        W_layer: [cout, cin_flat]  (pre-flattened)
        returns: Var_GL scalar = ||W - W_polar_S||^2
        """
        ...

    def get_supported_weight_names(self, state_dict: Dict[str, Tensor]) -> List[str]:
        """Return sorted list of .weight param names passing SUPPORTED_LAYER_TYPES filter."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| orbit_ids (per layer) | [cout] | int64, row-norm rank |
| orbit_matrix | [N_total_rows, P] | binary membership; N_total_rows = sum of cout per layer |
| orbit_basis (U from SVD) | [D, P] | top-D right singular vectors |
| W_flat | [P] | flattened full model params |
| W_proj | [D] | projection coefficients |
| W_perm | [P] | reconstructed orbit-aligned component |
| W_layer | [cout, cin_flat] | single layer for polar decomp |

### Pseudo-code: get_orbit_basis()

```
INPUT: state_dict (reference checkpoint)
OUTPUT: orbit_basis [D, P]

1. weight_names = get_supported_weight_names(state_dict)
2. P = sum of numel for each weight in weight_names
3. orbit_matrix = zeros(0, P)  # accumulate rows
4. param_offsets = compute cumulative parameter offsets per layer
5. for each (name, weight) in weight_names:
     orbit_ids = orbit_computer.compute_orbit_id(weight, layer_type)  # [cout]
     w_flat_layer = _flatten_weight(weight, layer_type)                # [cout, cin_flat]
     for each unique orbit_id o in orbit_ids:
         mask = (orbit_ids == o)              # [cout] bool
         mean_row = w_flat_layer[mask].mean(0) # [cin_flat]
         orbit_row = zeros(P)
         orbit_row[layer_start:layer_end] = mean_row.flatten()
         orbit_matrix = vstack(orbit_matrix, orbit_row)
6. orbit_matrix = L2-normalize each row
7. _, _, Vt = SVD(orbit_matrix, full_matrices=False)  # Vt: [min(rows,P), P]
8. D = min(orbit_basis_dim, Vt.shape[0])
9. return Vt[:D, :]   # [D, P]
```

### Pseudo-code: compute_gl_orbit_projection_layer()

```
INPUT: W_layer [cout, cin_flat], layer_type str
OUTPUT: var_gl scalar

1. if cout == cin_flat:  # square matrix
     Q, S = polar(W_layer.numpy())   # W = Q @ S
     W_sym = S                        # symmetric part
   else:  # non-square: use rectangular polar decomp
     U, sigma, Vt = SVD(W_layer, full_matrices=False)
     Q = U @ Vt                       # orthogonal factor
     S = Vt.T @ diag(sigma) @ Vt     # symmetric factor (projected)
     W_sym = Q @ S
2. var_gl = ||W_layer - W_sym||^2     # Frobenius norm squared
3. return float(var_gl)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | orbit_basis_svd | flatten_weights, get_supported_weight_names, get_orbit_basis (orbit matrix + SVD) |
| L-3-2 | orbit_projections | compute_perm_orbit_projection, compute_gl_orbit_projection_layer (polar decomp) |

---

## A-4: VarianceDecomposer Core [Complexity: 13, Budget: 2]

**Applied**: Standard PyTorch

### API Signatures

```python
# variance_decomposer.py
from typing import Dict, List, Tuple
import torch, numpy as np
from torch import Tensor

class VarianceDecomposer:
    """Decomposes trajectory variance into Var_perm and Var_GL components."""

    def __init__(self, orbit_projector: "OrbitProjector", eps: float = 1e-8): ...

    def compute_trajectory_variance_ratio(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, float]:
        """Compute Var_perm / (Var_perm + Var_GL) for one model trajectory.
        trajectory: list of T state_dicts, T >= min_checkpoints
        returns: {ratio, var_perm, var_gl, n_checkpoints}
        """
        ...

    def compute_epoch_ratios(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> List[float]:
        """Per-epoch ratio: ratio at each checkpoint t vs reference t=0.
        returns: list of T floats
        """
        ...

    def compute_layer_breakdown(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, Dict[str, float]]:
        """Per-layer-type (Conv2d vs Linear) Var_perm and Var_GL breakdown.
        returns: {'Conv2d': {var_perm, var_gl, ratio}, 'Linear': {...}}
        """
        ...

def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict[str, bool]]:
    """Check mechanism activation indicators. Fail-fast if any False.
    Checks: n_trajectories > 100, orbit_basis_dim > 0,
            0.0 <= var_ratio <= 1.0, var_perm > 0 and var_gl > 0
    returns: (all_pass bool, {indicator_name: bool})
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| W_flat_t | [P] | flattened params at checkpoint t |
| orbit_basis | [D, P] | from get_orbit_basis(trajectory[0]) |
| proj_coeffs | [D] | W_flat @ orbit_basis.T |
| W_perm | [P] | orbit_basis.T @ proj_coeffs |
| var_perm_t | scalar | ||W_perm||^2 at checkpoint t |
| var_gl_t | scalar | sum of per-layer GL variance |

### Pseudo-code: compute_trajectory_variance_ratio()

```
INPUT: trajectory (T state_dicts)
OUTPUT: {ratio, var_perm, var_gl, n_checkpoints}

1. orbit_basis = orbit_projector.get_orbit_basis(trajectory[0])   # [D, P]
2. var_perm_total = 0.0;  var_gl_total = 0.0
3. for each state_dict in trajectory:
     W_flat = orbit_projector.flatten_weights(state_dict)          # [P]
     # Permutation orbit variance
     W_perm, var_perm_t = orbit_projector.compute_perm_orbit_projection(W_flat, orbit_basis)
     var_perm_total += var_perm_t
     # GL orbit variance (summed over all layers)
     for name in orbit_projector.get_supported_weight_names(state_dict):
         W_layer = _flatten_weight(state_dict[name], layer_type)   # [cout, cin_flat]
         var_gl_total += orbit_projector.compute_gl_orbit_projection_layer(W_layer, layer_type)
4. ratio = var_perm_total / (var_perm_total + var_gl_total + eps)
5. return {ratio, var_perm_total, var_gl_total, n_checkpoints=len(trajectory)}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | trajectory_variance_ratio | compute_trajectory_variance_ratio, verify_mechanism_activated |
| L-4-2 | epoch_layer_breakdown | compute_epoch_ratios, compute_layer_breakdown |

---

## A-5: Evaluate Pipeline [Complexity: 11, Budget: 1]

### API Signatures

```python
# evaluate.py
from typing import Dict, List, Optional
import numpy as np

def run_zoo_analysis(
    dataset: "TrajectoryDataset",
    decomposer: "VarianceDecomposer",
    subset_name: str,
    min_models: int = 200,
) -> Dict:
    """Run variance decomposition on all trajectories.
    returns: {ratios: List[float], ratio_mean, ratio_std, n_models, subset_name,
              epoch_ratios: List[List[float]], layer_stats: Dict}
    """
    ...

def compute_cross_dataset_stability(
    ratio_cifar10: float, ratio_svhn: float
) -> Dict[str, float]:
    """Compute |ratio_CIFAR10 - ratio_SVHN|.
    returns: {stability_gap, ratio_cifar10, ratio_svhn}
    """
    ...

def check_gate(
    results_cifar10: Dict, results_svhn: Dict,
    threshold: float = 0.60, stability_threshold: float = 0.10
) -> Dict[str, bool]:
    """Evaluate MUST_WORK gate conditions.
    returns: {primary_pass, n_models_pass, non_degenerate_pass, stability_pass, all_pass}
    """
    ...

def save_results_json(results: Dict, output_path: str) -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | evaluate_pipeline | run_zoo_analysis, check_gate, save_results_json |

---

## A-6: Visualization [Complexity: 9, Budget: 1]

### API Signatures

```python
# visualize.py
from pathlib import Path
from typing import Dict, List

def plot_gate_bar_chart(
    results_cifar10: Dict, results_svhn: Dict,
    threshold: float, output_path: Path
) -> None:
    """Mandatory gate figure: Var_perm/Var_GL bars + 0.60 threshold line."""
    ...

def plot_ratio_histogram(
    ratios_cifar10: List[float], ratios_svhn: List[float], output_path: Path
) -> None: ...

def plot_ratio_vs_epoch(
    epoch_ratios: List[List[float]], output_path: Path
) -> None: ...

def plot_layer_breakdown(layer_stats: Dict, output_path: Path) -> None: ...

def plot_ratio_vs_accuracy(
    ratios: List[float], accuracies: List[float], output_path: Path
) -> None: ...

def save_all_figures(results: Dict, figures_dir: Path) -> None:
    """Generate and save all 5 required figures."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | visualization | All 5 figure functions + save_all_figures |

---

## A-7: run_experiment.py & Validation Report [Complexity: 10, Budget: 1]

### API Signatures

```python
# run_experiment.py
from typing import Dict

def setup_paths(config: "ExperimentConfig") -> None:
    """Create figures_dir, results_dir; verify h_m1_code_path exists."""
    ...

def run(config: "ExperimentConfig") -> Dict:
    """Full pipeline: load -> decompose -> evaluate -> visualize -> report.
    returns: gate_results dict
    """
    ...

def generate_validation_report(results: Dict, output_path: str) -> None:
    """Write 04_validation.md with PASS/PIVOT determination."""
    ...

if __name__ == "__main__":
    config = get_config()
    results = run(config)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_and_report | setup_paths, run(), generate_validation_report |

---

## Subtask Budget Summary

| Epic | Allocated | Used |
|------|-----------|------|
| A-1 | 1 | 1 |
| A-2 | 1 | 1 |
| A-3 | 2 | 2 |
| A-4 | 2 | 2 |
| A-5 | 1 | 1 |
| A-6 | 1 | 1 |
| A-7 | 1 | 1 |
| **Total** | **7** | **7** |
