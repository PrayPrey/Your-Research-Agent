# Config: H-M1
# Orbit-PE Mechanism Verification — Benchmark Configuration

**Hypothesis**: H-M1 (MECHANISM — INCREMENTAL on H-E1)
**Date**: 2026-05-21
**Type**: No-training benchmark

Applied: base-hypothesis-incremental dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (direct file read of h-e1/code/config.py)
**Config Files Found**: `docs/youra_research/20260521_wsl/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260521_wsl/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    figures_dir: str = "figures/"
    results_path: str = "outputs/results.json"
    n_cnn_checkpoints: int = 200
    n_transformer_checkpoints: int = 250
    n_permutations: int = 10
    perm_seeds: List[int] = field(default_factory=lambda: list(range(10)))
    sample_seed: int = 42
    eval_batch_size: int = 256
    delta_acc_threshold: float = 0.001
    device: str = "cuda"
```

**Verified from**: `docs/youra_research/20260521_wsl/h-e1/code/config.py` (actual implementation)

### Changes in H-M1

- `n_cnn_checkpoints`: 200 → 100 (benchmark uses subset)
- `n_transformer_checkpoints`: 250 → 100 (benchmark uses subset)
- Removed: `n_permutations`, `perm_seeds`, `eval_batch_size`, `delta_acc_threshold` (not needed for timing benchmark)
- Added: `token_dim`, `orbit_embed_dim`, `overhead_threshold`, `transformer_mnist_dir`, `n_transformer_mnist`
- `device`: "cuda" → "cpu" (timing benchmark, CPU for reproducible wall-clock)

---

## A-2: Config Module [Complexity: 4, Low]

**Applied**: Standard PyTorch defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Optional
import yaml
import os


@dataclass
class BenchmarkConfig:
    # Data paths (relative to code/ directory)
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    transformer_mnist_dir: str = "data/transformer_zoo/mnist/"
    figures_dir: str = "figures/"
    results_path: str = "outputs/results.json"

    # Checkpoint counts
    n_cnn_checkpoints: int = 100
    n_transformer_checkpoints: int = 100
    n_transformer_mnist: int = 100  # Non-standard: separate MNIST count for TransformerZooLoader

    # Sampling
    sample_seed: int = 42

    # OrbitPEComputer settings
    token_dim: int = 64
    orbit_embed_dim: int = 64  # Non-standard: set equal to token_dim for dim_consistent gate check

    # Benchmark gate threshold
    overhead_threshold: float = 1.2  # Non-standard: H-M1 gate requires orbit_PE overhead < 1.2x vanilla

    # Device
    device: str = "cpu"  # Non-standard: CPU for reproducible wall-clock timing


def load_config(config_path: str = None) -> BenchmarkConfig:
    """Load config from YAML file, overriding dataclass defaults."""
    cfg = BenchmarkConfig()
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        if data:
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
    return cfg
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | BenchmarkConfig impl | Implement BenchmarkConfig dataclass + load_config() with YAML override support |

---

## A-4: SequentialPEBaseline [Complexity: 9, Medium] → 1 subtask

**Applied**: Standard PyTorch defaults

### Configuration

No dedicated config class needed. `SequentialPEBaseline` takes `token_dim` from `BenchmarkConfig.token_dim` (default: 64).

```python
# Instantiation pattern (from run_experiment.py)
baseline = SequentialPEBaseline(token_dim=cfg.token_dim)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | SequentialPEBaseline impl | Implement SANE [n,l,k] sequential-PE replication with forward() returning per-layer (cout, token_dim) tensors |

---

## A-3: OrbitPEComputer [Complexity: 14, High]

**Applied**: Standard PyTorch defaults

### Configuration

`OrbitPEComputer` takes `token_dim` and `orbit_embed_dim` from `BenchmarkConfig`.

```python
# Instantiation pattern (from run_experiment.py)
orbit_computer = OrbitPEComputer(
    token_dim=cfg.token_dim,
    orbit_embed_dim=cfg.orbit_embed_dim,
)
```

No separate config class — parameters flow from `BenchmarkConfig`.

---

## Summary: Config Flow

```
BenchmarkConfig
  ├── token_dim=64          → OrbitPEComputer(token_dim=64, orbit_embed_dim=64)
  ├── token_dim=64          → SequentialPEBaseline(token_dim=64)
  ├── n_cnn_checkpoints=100 → CNNZooLoader(n_checkpoints=100)
  ├── n_transformer_mnist=100 → TransformerZooLoader(n_mnist=100)
  ├── overhead_threshold=1.2 → gate check in compute_gate_metrics()
  └── sample_seed=42        → loader sampling reproducibility
```
