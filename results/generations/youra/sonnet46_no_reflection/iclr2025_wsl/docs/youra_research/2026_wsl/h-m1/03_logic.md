# Logic: H-M1
# Orbit-PE Mechanism Verification — Unified Codebase & Overhead Constraint

**Hypothesis**: H-M1 (MECHANISM — INCREMENTAL on H-E1)
**Date**: 2026-05-21

Applied: dispatch dict pattern (no if/else), perf_counter timing benchmark

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code (Serena LSP unavailable — direct file read used)
**Analyzed Path**: `docs/youra_research/20260521_wsl/h-e1/code/`
**Relevant Symbols**:
- `compute_orbit_pe(state_dict, layer_type_map, n_heads=1)` → `(Dict[str, Tensor], Dict[str, bool])`
- `_infer_type_from_name(param_name, weight)` → `str`
- `get_layer_type_map(model)` → `Dict[str, str]`
- `CNNZooLoader.__init__(zoo_dir, n_checkpoints=200, seed=42)` — n_checkpoints default 200 in h-e1
- `TransformerZooLoader.__init__(mnist_dir, agnews_dir=None, n_mnist=250, n_agnews=0, seed=42)`
- `TransformerZooLoader.load_checkpoints()` → `List[{state_dict, val_acc, checkpoint_id, task, arch_config}]`
- `CNNZooLoader.load_checkpoints()` → `List[{state_dict, val_acc, checkpoint_id, task}]`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/orbit_pe.py (ACTUAL CODE)
SUPPORTED_LAYER_TYPES = ["Linear", "Conv2d", "MultiheadAttention"]

def compute_orbit_pe(
    state_dict: Dict[str, Tensor],
    layer_type_map: Dict[str, str],
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    """orbit_vector shape: [3] per weight param."""
    ...

def _infer_type_from_name(param_name: str, weight: Tensor) -> str:
    """Returns "Conv2d" | "MultiheadAttention" | "Linear" | "Unknown"."""
    ...

def get_layer_type_map(model: nn.Module) -> Dict[str, str]:
    """Returns param_name -> layer_type for named modules."""
    ...

# From: h-e1/code/data_loader.py (ACTUAL CODE)
class CNNZooLoader:
    def __init__(self, zoo_dir: str, n_checkpoints: int = 200, seed: int = 42): ...
    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns: [{state_dict, val_acc, checkpoint_id, task}]"""
        ...

class TransformerZooLoader:
    def __init__(
        self,
        mnist_dir: str,
        agnews_dir: str = None,
        n_mnist: int = 250,
        n_agnews: int = 0,
        seed: int = 42,
    ): ...
    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns: [{state_dict, val_acc, checkpoint_id, task, arch_config}]"""
        ...
```

**Verified from**: `docs/youra_research/20260521_wsl/h-e1/code/` (actual implementation)

**Key difference from architecture spec**: `CNNZooLoader` default is `n_checkpoints=200` (not 100). H-M1 must pass `n_checkpoints=100` explicitly. `TransformerZooLoader` uses `n_mnist` param (not `n_checkpoints`).

---

## A-3: OrbitPEComputer [Complexity: 14, Budget: 4 subtasks]

Applied: dispatch dict pattern (HAS_ARCH_BRANCHES = False)

### API Signatures

```python
# orbit_pe_computer.py
import torch
import torch.nn as nn
from torch import Tensor
from typing import Dict, List, Optional, Tuple

HAS_ARCH_BRANCHES: bool = False  # module-level flag — code inspection gate criterion

class OrbitPEComputer(nn.Module):
    def __init__(self, token_dim: int, orbit_embed_dim: int = 64):
        """Init embedding table for orbit IDs -> token_dim vectors."""
        ...

    def compute_orbit_id(self, weight: Tensor, layer_type: str) -> Tensor:
        """
        Compute permutation-invariant orbit IDs via row-norm rank.
        weight: [cout, cin] | [cout, cin, kH, kW] | [cout, cin] after head-flatten
        returns: [cout] int64 orbit IDs (rank of row norms, 0-indexed)
        """
        ...

    def forward(self, weight: Tensor, layer_type: str) -> Tensor:
        """
        weight: [cout, cin] | [cout, cin, kH, kW]
        returns: [cout, token_dim]
        """
        ...


def _flatten_weight(weight: Tensor, layer_type: str, n_heads: int = 1) -> Tensor:
    """
    Normalize all weight shapes to [cout, cin] 2D for unified orbit computation.
    Conv2d [cout, cin, kH, kW] -> [cout, cin*kH*kW]
    MHA [cout, cin] with n_heads > 1 -> head-flatten [n_heads*head_dim, cin] (no-op if already 2D)
    Linear [cout, cin] -> unchanged
    returns: [cout, cin_flat]
    """
    ...


def compute_orbit_pe_all_layers(
    state_dict: Dict[str, Tensor],
    orbit_computer: "OrbitPEComputer",
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    """
    Iterate all .weight params in state_dict, dispatch to orbit_computer.
    Infers layer type via _infer_type_from_name (from h-e1).
    returns: (orbit_vecs {param_name -> [cout, token_dim]}, success_flags {param_name -> bool})
    Logs: "OrbitPE computed for layer {name} (type={layer_type}): dim={orbit_dim}"
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight (Linear) | [cout, cin] | Input to compute_orbit_id |
| weight (Conv2d) | [cout, cin, kH, kW] | Flattened to [cout, cin*kH*kW] |
| weight (MHA) | [cout, cin] | Already 2D; head-flatten is identity |
| row_norms | [cout] | L2 norm along dim=1 of flattened weight |
| orbit_ids | [cout] | argsort(argsort(row_norms)) — rank order |
| pe_out | [cout, token_dim] | Output of forward() |

### Pseudo-code (compute_orbit_id)

```
1. w_flat = _flatten_weight(weight, layer_type)   # [cout, cin_flat]
2. row_norms = w_flat.norm(dim=1)                 # [cout]
3. sorted_idx = argsort(row_norms)                # [cout]
4. orbit_ids = zeros_like(sorted_idx)
5. orbit_ids[sorted_idx] = arange(cout)           # rank assignment
6. return orbit_ids.long()                        # [cout]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | _flatten_weight | Normalize Conv2d/MHA/Linear to [cout, cin_flat] |
| L-3-2 | compute_orbit_id | Row-norm rank as permutation-invariant orbit IDs |
| L-3-3 | OrbitPEComputer.forward | Embedding lookup + HAS_ARCH_BRANCHES flag |
| L-3-4 | compute_orbit_pe_all_layers | State dict iteration with dispatch + logging |

---

## A-6: Benchmark Loop [Complexity: 12, Budget: 2 subtasks]

Applied: time.perf_counter() wall-clock pattern

### API Signatures

```python
# benchmark.py
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class CheckpointResult:
    checkpoint_id: str
    arch_family: str           # "cnn" | "transformer"
    t_vanilla: float           # seconds
    t_orbit: float             # seconds
    overhead_ratio: float      # t_orbit / t_vanilla
    success: bool
    layer_types_seen: List[str]
    error: Optional[str] = None


def _time_vanilla(
    state_dict: Dict,
    baseline: "SequentialPEBaseline",
) -> float:
    """Returns wall-clock seconds for one checkpoint via time.perf_counter()."""
    ...


def _time_orbit(
    state_dict: Dict,
    orbit_computer: "OrbitPEComputer",
    n_heads: int = 1,
) -> Tuple[float, bool, List[str]]:
    """Returns (seconds, success, layer_types_seen)."""
    ...


def run_timing_benchmark(
    cnn_checkpoints: List[Dict],
    transformer_checkpoints: List[Dict],
    orbit_computer: "OrbitPEComputer",
    baseline: "SequentialPEBaseline",
    cfg: "BenchmarkConfig",
) -> List[CheckpointResult]:
    """
    For each checkpoint in cnn_checkpoints + transformer_checkpoints:
      t0 = time.perf_counter(); compute_sequential_pe_all(...); t_vanilla = perf_counter() - t0
      t0 = time.perf_counter(); compute_orbit_pe_all_layers(...); t_orbit = perf_counter() - t0
      overhead_ratio = t_orbit / max(t_vanilla, 1e-9)
    Returns List[CheckpointResult] length == len(cnn) + len(transformer).
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | _time_vanilla / _time_orbit | perf_counter wrappers, error handling |
| L-6-2 | run_timing_benchmark loop | Iterate CNN+Transformer, build CheckpointResult list |

---

## A-9: Run Experiment [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch entrypoint pattern

### API Signatures

```python
# run_experiment.py
import sys, os, json, time
import torch

def main(config_path: str = None) -> bool:
    """
    1. load_config(config_path) -> BenchmarkConfig
    2. CNNZooLoader(cfg.cnn_zoo_dir, n_checkpoints=cfg.n_cnn_checkpoints, seed=cfg.sample_seed).load_checkpoints()
    3. TransformerZooLoader(cfg.transformer_mnist_dir, n_mnist=cfg.n_transformer_checkpoints, seed=cfg.sample_seed).load_checkpoints()
    4. OrbitPEComputer(token_dim=cfg.token_dim)
    5. SequentialPEBaseline(token_dim=cfg.token_dim)
    6. run_timing_benchmark(cnn_ckpts, tf_ckpts, orbit_computer, baseline, cfg)
    7. compute_gate_metrics(results, has_arch_branches=HAS_ARCH_BRANCHES)
    8. save_metrics(metrics, cfg.results_path)
    9. generate_validation_report(metrics, output_path="04_validation.md")
    10. save_all_figures(results, metrics, cfg.figures_dir)
    returns: gate_pass bool
    """
    ...

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

**Critical parameter mapping** (verified from h-e1 actual code):
- `CNNZooLoader(n_checkpoints=cfg.n_cnn_checkpoints)` — must be 100, not default 200
- `TransformerZooLoader(n_mnist=cfg.n_transformer_checkpoints)` — uses `n_mnist` kwarg, not `n_checkpoints`

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | main() entrypoint | Wire all modules, correct loader kwargs |
| L-9-2 | End-to-end error handling | Try/except per checkpoint, fallback n_checkpoints |

---

## A-7: Gate Metrics + Validation [Complexity: 10, Budget: 1 subtask]

Applied: Standard PyTorch evaluation pattern

### API Signatures

```python
# evaluate.py
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class GateMetrics:
    computability_rate: float          # fraction of checkpoints where success=True
    unified_codebase: bool             # == not HAS_ARCH_BRANCHES
    overhead_ratio_mean: float
    overhead_ratio_std: float
    dim_consistent: bool               # all pe_out.shape[-1] == token_dim
    per_layer_overhead: Dict[str, float]  # mean overhead per layer_type seen


def compute_gate_metrics(
    results: List["CheckpointResult"],
    has_arch_branches: bool = False,
) -> GateMetrics:
    """
    computability_rate = sum(r.success for r in results) / len(results)
    overhead_ratio_mean/std from [r.overhead_ratio for r in results]
    per_layer_overhead: group results by layer_types_seen, average overhead_ratio
    dim_consistent: True (checked inside orbit_computer.forward)
    """
    ...


def verify_orbit_pe_activated(
    checkpoint_results: Dict,
) -> Tuple[bool, Dict]:
    """
    Checks that orbit_pe was called for all checkpoints.
    Returns (all_activated: bool, details: Dict).
    """
    ...


def save_metrics(metrics: GateMetrics, path: str) -> None:
    """Serialize GateMetrics to JSON at path."""
    ...


def generate_validation_report(
    metrics: GateMetrics,
    output_path: str,
) -> None:
    """
    Write 04_validation.md.
    PASS if: computability_rate==1.0 AND unified_codebase==True AND overhead_ratio_mean<=1.2
    FAIL otherwise.
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_gate_metrics + generate_validation_report | Aggregate results, write PASS/FAIL report |
