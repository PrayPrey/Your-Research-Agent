# Configuration: H-M2
# Permutation Orbit Variance Dominance — Var_perm / (Var_perm + Var_GL) > 0.60

Applied: dataclass + YAML-override pattern (from h-m1 BenchmarkConfig / load_config pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 incremental)
**Status**: Config classes verified from base code (direct file read)
**Config Files Found**: `docs/youra_research/20260521_wsl/h-m1/code/config.py`, `docs/youra_research/20260521_wsl/h-m1/code/config.yaml`
**Pattern Used**: dataclass with YAML override via `load_config(path)`

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m1 Code)

```python
# From: docs/youra_research/20260521_wsl/h-m1/code/config.py (ACTUAL CODE)
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
    orbit_embed_dim: int = 64
    overhead_threshold: float = 1.2
    device: str = "cpu"
```

**Verified from**: `docs/youra_research/20260521_wsl/h-m1/code/config.py` (actual implementation)

### Reuse vs New

| Field | Status | Notes |
|-------|--------|-------|
| `token_dim` | Inherited (renamed) | h-m1: `token_dim=64`; kept as-is |
| `orbit_embed_dim` | Inherited (renamed to `orbit_basis_dim`) | h-m1: `orbit_embed_dim=64` |
| `sample_seed` | Inherited (renamed to `seed`) | h-m1: `sample_seed=42`; h-m2 uses `seed=1` (deterministic SVD) |
| `device` | Inherited | `"cpu"` — h-m2 is CPU-bound SVD |
| `figures_dir` | Replaced | h-m2 has dataset-namespaced path |
| `results_path` | Replaced | h-m2 uses `results_dir/` folder |
| `data_dir_cifar10` | New | Two separate zoo datasets |
| `data_dir_svhn` | New | SVHN-GS secondary dataset |
| `h_m1_code_path` | New | Path to h-m1 code for sys.path import |
| `min_models` | New | Gate: ≥200 models required |
| `min_checkpoints` | New | Filter: skip trajectories shorter than 10 |
| `max_checkpoints` | New | Memory guard: subsample to ≤50 |
| `n_epochs` | New | 51 (epochs 0..50) |
| `gate_threshold` | New | 0.60 primary gate |
| `stability_threshold` | New | 0.10 cross-dataset gap |
| `eps` | New | 1e-8 numerical stability |

---

## A-1: Setup & Data Preparation [Complexity: 7, Budget: 1]

**Applied**: Standard paths-only config section

### Configuration

```python
# Covered by ExperimentConfig paths section below
# No additional config needed for A-1
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | SetupConfig | Create config.py and config.yaml; mkdir figures/ results/; verify h-m1 path |

---

## A-2: TrajectoryDataset [Complexity: 8, Budget: 1]

**Applied**: Standard dataset config fields (min/max checkpoints)

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | DataloaderConfig | Implement TrajectoryDataset using min_checkpoints, max_checkpoints, n_epochs from ExperimentConfig |

---

## A-3: OrbitProjector Wrapper [Complexity: 14, Budget: 1]

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ProjectorConfig | OrbitProjector reads token_dim, orbit_basis_dim, h_m1_code_path from ExperimentConfig |

---

## A-4: VarianceDecomposer Core [Complexity: 13, Budget: 1]

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | DecomposerConfig | VarianceDecomposer reads eps from ExperimentConfig |

---

## A-5: Evaluate Pipeline [Complexity: 11, Budget: 2]

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ZooAnalysisLoop | run_zoo_analysis uses min_models, max_checkpoints; streams trajectories sequentially |
| C-5-2 | GateCheck | check_gate uses gate_threshold=0.60, stability_threshold=0.10; save_results_json to results_dir |

---

## A-6: Visualization [Complexity: 9, Budget: 2]

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | GateFigures | plot_gate_bar_chart, plot_ratio_histogram, plot_layer_breakdown using gate_threshold; output to figures_dir |
| C-6-2 | TrajectoryFigures | plot_ratio_vs_epoch, plot_ratio_vs_accuracy; save_all_figures orchestrator |

---

## A-7: RunExperiment & Validation Report [Complexity: 10, Budget: 2]

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | PipelineWiring | run() wires all modules; setup_paths creates figures_dir and results_dir |
| C-7-2 | ValidationReport | generate_validation_report writes 04_validation.md with PASS/PIVOT determination |

---

## Full ExperimentConfig Dataclass

```python
"""ExperimentConfig for H-M2: Permutation Orbit Variance Dominance."""
from dataclasses import dataclass
from pathlib import Path
import yaml
import os


H_M1_CODE_PATH: str = "docs/youra_research/20260521_wsl/h-m1/code"


@dataclass
class ExperimentConfig:
    # Paths
    data_dir_cifar10: str = "data/cnn_zoo_cifar10"
    data_dir_svhn: str = "data/cnn_zoo_svhn"
    figures_dir: str = "docs/youra_research/20260521_wsl/h-m2/figures"
    results_dir: str = "docs/youra_research/20260521_wsl/h-m2/results"
    h_m1_code_path: str = H_M1_CODE_PATH

    # Data / trajectory parameters
    min_models: int = 200
    min_checkpoints: int = 10
    max_checkpoints: int = 50
    n_epochs: int = 51

    # Orbit projection parameters
    orbit_basis_dim: int = 64   # Non-standard: matches h-m1 token_dim=64 (orbit embedding size)
    token_dim: int = 64

    # Experiment control
    seed: int = 1               # Non-standard: seed=1 (not 42) for deterministic SVD reproducibility
    device: str = "cpu"

    # Gate thresholds
    gate_threshold: float = 0.60
    stability_threshold: float = 0.10
    eps: float = 1e-8


def get_config(config_path: str = None) -> ExperimentConfig:
    """Load config from YAML file, overriding dataclass defaults."""
    cfg = ExperimentConfig()
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

---

## YAML Config Schema (config.yaml)

```yaml
# H-M2 ExperimentConfig — override defaults here

# Paths
data_dir_cifar10: "data/cnn_zoo_cifar10"
data_dir_svhn: "data/cnn_zoo_svhn"
figures_dir: "docs/youra_research/20260521_wsl/h-m2/figures"
results_dir: "docs/youra_research/20260521_wsl/h-m2/results"
h_m1_code_path: "docs/youra_research/20260521_wsl/h-m1/code"

# Data / trajectory
min_models: 200
min_checkpoints: 10
max_checkpoints: 50
n_epochs: 51

# Orbit projection
orbit_basis_dim: 64
token_dim: 64

# Experiment control
seed: 1
device: "cpu"

# Gate thresholds
gate_threshold: 0.60
stability_threshold: 0.10
eps: 1.0e-8
```

---

## Parameter Sensitivity Table

Which parameters affect the gate metric `var_ratio_mean > 0.60`:

| Parameter | Affects Gate | Sensitivity | Notes |
|-----------|-------------|-------------|-------|
| `orbit_basis_dim` | High | Changing D changes subspace size; lower D → lower Var_perm | Keep at 64 (matches h-m1 token_dim) |
| `max_checkpoints` | Medium | More checkpoints = more trajectory coverage; too few may miss variance | 50 is memory-safe fallback |
| `min_models` | Medium | Gate requires ≥200; affects mean/std estimate stability | 200 is hard floor |
| `eps` | Low | Only affects numerical stability in denominator; no semantic effect | 1e-8 is standard |
| `gate_threshold` | N/A | Defines pass/fail boundary, not the metric itself | Fixed at 0.60 per hypothesis |
| `stability_threshold` | N/A | Secondary criterion boundary | Fixed at 0.10 per hypothesis |
| `seed` | Low | SVD is deterministic; seed controls only random subsampling if used | seed=1 for reproducibility |
| `min_checkpoints` | Low | Only affects which models are included; changes sample size | 10 is liberal filter |
