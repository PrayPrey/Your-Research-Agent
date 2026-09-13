# Architecture: H-M1
# Orbit-PE Mechanism Verification — Unified Codebase & Overhead Constraint

**Hypothesis**: H-M1 (MECHANISM — INCREMENTAL on H-E1)
**Date**: 2026-05-21
**Type**: Computability + timing benchmark (no training)

Applied: base-hypothesis-incremental pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (Glob + direct Read used; Serena LSP unavailable — no active project context)
**Analyzed Path**: `docs/youra_research/20260521_wsl/h-e1/code/`
**Findings**: H-E1 has `orbit_pe.py` with `compute_orbit_pe()` using dispatch dict (no if/else branches), `data_loader.py` with `CNNZooLoader` / `TransformerZooLoader` (Ray Tune + pt format), `config.py` with `ExperimentConfig` dataclass, `run_experiment.py`, `evaluate.py`, `permutation.py`, `visualize.py`. H-M1 reuses loaders and orbit_pe primitives with extensions for timing benchmark and `OrbitPEComputer` nn.Module wrapper.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CNNZooLoader | `from h_e1.data_loader import CNNZooLoader` | `h-e1/code/data_loader.py` |
| TransformerZooLoader | `from h_e1.data_loader import TransformerZooLoader` | `h-e1/code/data_loader.py` |
| compute_orbit_pe | `from h_e1.orbit_pe import compute_orbit_pe` | `h-e1/code/orbit_pe.py` |
| get_layer_type_map | `from h_e1.orbit_pe import get_layer_type_map` | `h-e1/code/orbit_pe.py` |
| _infer_type_from_name | `from h_e1.orbit_pe import _infer_type_from_name` | `h-e1/code/orbit_pe.py` |

**Note**: H-M1 code will be in `h-m1/code/`. Imports from h-e1 are resolved by adding `h-e1/code/` to sys.path or by copying/symlinking. Architecture prefers copying relevant files into `h-m1/code/` to keep the codebase self-contained.

**Verified from**: `docs/youra_research/20260521_wsl/h-e1/code/` (actual implementation)

---

## File Organization

- `h-m1/code/`
  - `config.py` — BenchmarkConfig dataclass
  - `orbit_pe_computer.py` — OrbitPEComputer nn.Module (new, H-M1 core)
  - `sequential_pe_baseline.py` — SequentialPEBaseline (vanilla SANE timing reference)
  - `data_loader.py` — copied + adapted from h-e1 (100 CNN + 100 Transformer)
  - `benchmark.py` — timing loop over 200 checkpoints
  - `evaluate.py` — gate metrics computation + verify_orbit_pe_activated()
  - `visualize.py` — bar chart + box plots
  - `run_experiment.py` — main entrypoint
  - `outputs/` — results.json
  - `data/` — cnn_zoo/, transformer_zoo/

---

## Modules

### BenchmarkConfig (`config.py`)

**Dependencies**: stdlib only

```python
@dataclass
class BenchmarkConfig:
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    transformer_mnist_dir: str = "data/transformer_zoo/mnist/"
    figures_dir: str = "figures/"
    results_path: str = "outputs/results.json"
    n_cnn_checkpoints: int = 100
    n_transformer_checkpoints: int = 100
    n_transformer_mnist: int = 100
    sample_seed: int = 42
    token_dim: int = 64
    overhead_threshold: float = 1.2
    device: str = "cpu"

def load_config(config_path: str = None) -> BenchmarkConfig: ...
```

---

### OrbitPEComputer (`orbit_pe_computer.py`)

**Dependencies**: torch, h-e1 orbit_pe primitives (copied)

```python
class OrbitPEComputer(nn.Module):
    def __init__(self, token_dim: int, orbit_embed_dim: int): ...
    def compute_orbit_id(self, weight: Tensor, layer_type: str) -> Tensor:
        """
        weight: (cout, cin) | (cout, cin, kH, kW) | (cout, cin) after head-flatten
        returns: (cout,) int tensor of orbit IDs
        """
        ...
    def forward(self, weight: Tensor, layer_type: str) -> Tensor:
        """returns: (cout, token_dim) — same shape as SANE sequential-PE"""
        ...

def compute_orbit_pe_all_layers(
    state_dict: Dict[str, Tensor],
    orbit_computer: OrbitPEComputer,
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    """Iterate all weight params, dispatch to orbit_computer. Returns (orbit_vecs, success_flags)."""
    ...

HAS_ARCH_BRANCHES: bool = False  # module-level flag for code inspection
```

---

### SequentialPEBaseline (`sequential_pe_baseline.py`)

**Dependencies**: torch

```python
class SequentialPEBaseline(nn.Module):
    def __init__(self, token_dim: int): ...
    def forward(self, state_dict: Dict[str, Tensor]) -> Dict[str, Tensor]:
        """
        Replicates SANE sequential [n, l, k] position encoding.
        Returns dict param_name -> (cout, token_dim) pe tensor.
        """
        ...

def compute_sequential_pe_all(
    state_dict: Dict[str, Tensor],
    baseline: SequentialPEBaseline,
) -> Dict[str, Tensor]:
    """Convenience wrapper. Returns pe_vectors dict."""
    ...
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: torch, numpy, glob, json (copied from h-e1 with n_checkpoints adapted)

```python
class CNNZooLoader:
    def __init__(self, zoo_dir: str, n_checkpoints: int = 100, seed: int = 42): ...
    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task}."""
        ...

class TransformerZooLoader:
    def __init__(self, mnist_dir: str, n_mnist: int = 100, seed: int = 42): ...
    def load_checkpoints(self) -> List[Dict[str, Any]]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task, arch_config}."""
        ...
```

---

### Benchmark (`benchmark.py`)

**Dependencies**: BenchmarkConfig, OrbitPEComputer, SequentialPEBaseline, DataLoader, time

```python
@dataclass
class CheckpointResult:
    checkpoint_id: str
    arch_family: str          # "cnn" | "transformer"
    t_vanilla: float
    t_orbit: float
    overhead_ratio: float
    success: bool
    layer_types_seen: List[str]
    error: Optional[str]

def run_timing_benchmark(
    cnn_checkpoints: List[Dict],
    transformer_checkpoints: List[Dict],
    orbit_computer: OrbitPEComputer,
    baseline: SequentialPEBaseline,
    cfg: BenchmarkConfig,
) -> List[CheckpointResult]:
    """
    For each checkpoint:
      - time vanilla sequential-PE
      - time orbit-PE
      - record overhead_ratio, success
    Returns list of CheckpointResult.
    """
    ...
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: CheckpointResult, json

```python
@dataclass
class GateMetrics:
    computability_rate: float
    unified_codebase: bool
    overhead_ratio_mean: float
    overhead_ratio_std: float
    dim_consistent: bool
    per_layer_overhead: Dict[str, float]   # {Linear, Conv2d, MultiheadAttention}

def compute_gate_metrics(
    results: List[CheckpointResult],
    has_arch_branches: bool = False,
) -> GateMetrics: ...

def verify_orbit_pe_activated(
    checkpoint_results: Dict,
) -> Tuple[bool, Dict]: ...

def save_metrics(metrics: GateMetrics, path: str) -> None: ...

def generate_validation_report(
    metrics: GateMetrics,
    output_path: str,
) -> None:
    """Writes 04_validation.md with PASS/FAIL determination."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, CheckpointResult, GateMetrics

```python
def plot_overhead_per_layer_type(
    per_layer_overhead: Dict[str, float],
    threshold: float,
    save_path: str,
) -> None:
    """Bar chart: overhead_ratio per layer type vs 1.2x threshold line."""
    ...

def plot_overhead_distribution(
    results: List[CheckpointResult],
    save_path: str,
) -> None:
    """Box plots: overhead_ratio grouped by cnn vs transformer."""
    ...

def save_all_figures(
    results: List[CheckpointResult],
    metrics: GateMetrics,
    figures_dir: str,
) -> None: ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(config_path: str = None) -> None:
    """
    1. Load config
    2. Load 100 CNN + 100 Transformer checkpoints
    3. Init OrbitPEComputer + SequentialPEBaseline
    4. run_timing_benchmark()
    5. compute_gate_metrics()
    6. save_metrics() + generate_validation_report()
    7. save_all_figures()
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Setup | Clone repos, download 100 CNN + 100 Transformer checkpoints, verify file structure | 8 | 2+2+2+2 |
| A-2 | Config Module | Implement BenchmarkConfig dataclass + load_config() | 4 | 1+1+1+1 |
| A-3 | OrbitPEComputer | Implement nn.Module with compute_orbit_id + forward; unified dispatch (no if/else); HAS_ARCH_BRANCHES flag | 14 | 4+3+4+3 |
| A-4 | SequentialPEBaseline | Replicate SANE [n,l,k] sequential-PE for timing baseline | 9 | 2+2+3+2 |
| A-5 | DataLoader Adaptation | Copy h-e1 CNNZooLoader + TransformerZooLoader; adjust n_checkpoints=100 | 7 | 2+2+2+1 |
| A-6 | Benchmark Loop | Implement run_timing_benchmark() with time.perf_counter() per checkpoint; record CheckpointResult | 12 | 3+3+3+3 |
| A-7 | Gate Metrics + Validation | compute_gate_metrics(), verify_orbit_pe_activated(), save_metrics(), generate_validation_report() | 10 | 3+2+3+2 |
| A-8 | Visualization | Bar chart (overhead per layer type + threshold), box plots (CNN vs Transformer distribution) | 8 | 2+2+2+2 |
| A-9 | Run Experiment + Fix | run_experiment.py main(), end-to-end execution, debug failures, confirm gate pass/fail | 12 | 3+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-6, A-7, A-9, A-4], Low(4-8): [A-1, A-2, A-5, A-8]
