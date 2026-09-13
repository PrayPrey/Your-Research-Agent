# Configuration Specification: h-m1 Seed Independence

**Date:** 2026-03-21
**Hypothesis ID:** h-m1 (MECHANISM)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)

Applied: PyTorch deterministic reproducibility pattern, seed independence testing

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 base code
**Config Files Found:** `h-e1/code/config.py`
**Pattern Used:** dataclass

Verified actual field names and defaults from h-e1 implementation. H-M1 simplifies the config structure since it only tests initialization (no training).

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from base hypothesis:

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    """Configuration for variance measurement experiments."""

    # Experimental design
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    seeds: List[int] = field(default_factory=lambda: list(range(30)))

    # Training hyperparameters (not used in H-M1)
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    batch_size: int = 64

    # Determinism settings
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False

    # Paths
    data_root: str = "./data"
    results_dir: str = "./results"
    figures_dir: str = "./figures"
```

**Verified from:** `h-e1/code/config.py` (actual implementation)

---

## A-1: Configuration Setup [Complexity: 6, Budget: 2]

Applied: Simplified dataclass pattern for initialization-only experiment

### Configuration (Python Dataclass)

```python
"""Configuration for H-M1 Seed Independence Experiment."""

from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for seed independence testing."""

    # Experimental design
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])

    # Device settings
    device: str = "cuda"

    # Paths
    data_root: str = "./data"
    output_dir: str = "./results"
    figures_dir: str = "./figures"

    def __post_init__(self):
        """Ensure output directories exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class DeterminismConfig:
    """PyTorch determinism configuration."""

    cublas_workspace_config: str = ":16:8"
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False


def get_default_config() -> ExperimentConfig:
    """Return default experiment configuration."""
    return ExperimentConfig()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig | Seed range (0-29), datasets, architectures, paths |
| C-1-2 | DeterminismConfig | PyTorch determinism flags (cudnn, cublas workspace) |

---

## Configuration Values Summary

### Experimental Design
- **Seeds:** 0-29 (30 independent initializations)
- **Architectures:** ["1layer", "2layer"]
- **Datasets:** ["mnist", "fashion_mnist"]
- **Conditions:** 4 total (2 architectures × 2 datasets)

### Determinism Settings
- **cudnn_deterministic:** True
- **cudnn_benchmark:** False
- **CUBLAS_WORKSPACE_CONFIG:** ":16:8"

### Device Configuration
- **Device:** Single GPU (CUDA) or CPU fallback
- **GPU Selection:** Via CUDA_VISIBLE_DEVICES environment variable

### Output Paths
- **Data Root:** ./data/ (for dataset downloads)
- **Results Directory:** ./results/
  - pairwise_distances_{condition}.npy
  - statistics_{condition}.json
  - gate_result.json
- **Figures Directory:** ./figures/
  - gate_metrics_comparison.png (mandatory)
  - distance_distribution_{condition}.png
  - distance_heatmap_{condition}.png
  - condition_comparison.png

---

## Usage Example

```python
from config import ExperimentConfig, DeterminismConfig, get_default_config

# Option 1: Use defaults
config = get_default_config()

# Option 2: Customize
config = ExperimentConfig()
config.seeds = list(range(20))  # Only 20 seeds for testing
config.device = "cpu"  # Force CPU

# Get determinism config
det_config = DeterminismConfig()

# Setup experiment
print(f"Testing {len(config.seeds)} seeds")
print(f"Across {len(config.architectures)} architectures")
print(f"And {len(config.datasets)} datasets")
# Output: Testing 30 seeds, Across 2 architectures, And 2 datasets
```

---

## Differences from H-E1 Config

| Aspect | H-E1 | H-M1 |
|--------|------|------|
| **Purpose** | Training + variance measurement | Initialization testing only |
| **Config Complexity** | Nested dataclasses (7 sub-configs) | Flat dataclasses (2 total) |
| **Training Params** | epochs, lr, momentum, batch_size | Not needed |
| **Key Focus** | Variance metrics, gate threshold | Pairwise distances, t-test |
| **Reused Fields** | seeds, architectures, datasets, paths | Same |
| **New Fields** | None | DeterminismConfig (explicit separation) |

---

## Validation Checklist

- [x] ONE format only (dataclass)
- [x] Field names verified from h-e1 actual code
- [x] Inherited Configuration section included
- [x] Default values from research (PyTorch determinism docs)
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] EXISTENCE PoC: Single fixed config (no variations)

---

## Notes

**MECHANISM PoC Configuration:**
- Minimal config for initialization-only experiment
- No training hyperparameters needed
- 30 seeds for robust statistical testing (435 pairwise comparisons)
- Determinism flags separated into dedicated config class

**Non-Standard Values:**
- `cublas_workspace_config=":16:8"`: PyTorch determinism requirement for CUDA operations
- Smaller workspace than h-e1 (":16:8" vs ":4096:8") - sufficient for initialization

**Inherited from H-E1:**
- Seeds range (0-29)
- Architectures list (["1layer", "2layer"])
- Datasets list (["mnist", "fashion_mnist"])
- Path structure (data_root, output_dir, figures_dir)

---

*Generated by Phase 3 Config Agent*
*Hypothesis: h-m1 (MECHANISM) | Gate: MUST_WORK*
*Next: Phase 4 Implementation (Task Execution)*
