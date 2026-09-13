# Configuration Specification: h-m2 Trajectory Divergence

**Date:** 2026-03-21
**Hypothesis ID:** h-m2 (MECHANISM)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)

Applied: Statistical analysis configuration pattern, Artifact reuse configuration

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m1 base code
**Config Files Found:** `h-m1/code/config.py`
**Pattern Used:** dataclass

Verified actual field names and defaults from h-m1 implementation. H-M2 extends the pattern for analysis-only hypothesis that loads artifacts from h-m1.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from base hypothesis:

```python
# From: h-m1/code/config.py (ACTUAL CODE)
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
```

**Verified from:** `h-m1/code/config.py` (actual implementation)

---

## A-1: Environment Setup [Complexity: 5, Budget: 0]

Applied: Analysis-only configuration pattern (no training hyperparameters)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M2 Trajectory Divergence Analysis."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class H_M1_ArtifactConfig:
    """Configuration for loading h-m1 experiment artifacts."""

    h_m1_results_path: Path = field(default_factory=lambda: Path("../h-m1/results"))
    conditions: List[str] = field(
        default_factory=lambda: [
            "1layer_mnist",
            "1layer_fashion_mnist",
            "2layer_mnist",
            "2layer_fashion_mnist"
        ]
    )
    n_seeds: int = 30
    n_epochs: int = 10


@dataclass
class AnalysisConfig:
    """Configuration for trajectory divergence analysis."""

    # H-M1 artifact settings
    h_m1_config: H_M1_ArtifactConfig = field(default_factory=H_M1_ArtifactConfig)

    # Output paths
    output_dir: Path = field(default_factory=lambda: Path("./results"))
    figures_dir: Path = field(default_factory=lambda: Path("./figures"))

    # Statistical testing thresholds
    primary_alpha: float = 0.05
    secondary_cv_threshold: float = 1.0

    def __post_init__(self):
        """Ensure output directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)


def get_default_config() -> AnalysisConfig:
    """Return default analysis configuration."""
    return AnalysisConfig()
```

---

## Configuration Values Summary

### H-M1 Artifact Settings
- **h_m1_results_path:** `../h-m1/results` (relative path to h-m1 outputs)
- **conditions:** 4 conditions (1layer/2layer × mnist/fashion_mnist)
- **n_seeds:** 30 (inherited from h-m1)
- **n_epochs:** 10 (inherited from h-m1)

### Statistical Testing
- **primary_alpha:** 0.05 (p-value threshold for significance)
- **secondary_cv_threshold:** 1.0 (minimum CV percentage for trajectory divergence)

### Output Paths
- **output_dir:** `./results/`
  - analysis_results.json (per-condition metrics)
  - gate_validation.json (gate pass/fail status)
- **figures_dir:** `./figures/`
  - gate_metrics_comparison.png (required 4-panel figure)

---

## Artifact File Structure (Expected from H-M1)

```
h-m1/results/
├── 1layer_mnist/
│   ├── seed_0/
│   │   ├── initial_weights.pt    # torch tensor, flattened parameters
│   │   ├── final_weights.pt      # torch tensor, flattened parameters
│   │   └── loss_history.npy      # numpy array, shape (10,)
│   ├── seed_1/
│   ...
│   └── seed_29/
├── 1layer_fashion_mnist/
├── 2layer_mnist/
└── 2layer_fashion_mnist/
```

**Total Files:** 360 (30 seeds × 4 conditions × 3 artifact types)

---

## Usage Example

```python
from config import AnalysisConfig, get_default_config

# Option 1: Use defaults
config = get_default_config()

# Option 2: Customize paths
config = AnalysisConfig()
config.h_m1_config.h_m1_results_path = Path("/absolute/path/to/h-m1/results")
config.output_dir = Path("./custom_results")

# Verify h-m1 artifact path exists
if not config.h_m1_config.h_m1_results_path.exists():
    raise FileNotFoundError(f"H-M1 results not found: {config.h_m1_config.h_m1_results_path}")

# Expected artifact counts
expected_files = config.h_m1_config.n_seeds * len(config.h_m1_config.conditions) * 3
print(f"Expecting {expected_files} artifact files from h-m1")
# Output: Expecting 360 artifact files from h-m1
```

---

## Differences from H-M1 Config

| Aspect | H-M1 | H-M2 |
|--------|------|------|
| **Purpose** | Initialization testing (no training) | Artifact analysis (no training) |
| **Config Structure** | ExperimentConfig + DeterminismConfig | AnalysisConfig + H_M1_ArtifactConfig |
| **Key Fields** | seeds, architectures, datasets, device | h_m1_results_path, conditions, thresholds |
| **Paths** | data_root, output_dir, figures_dir | output_dir, figures_dir (no data_root) |
| **Device** | cuda/cpu | Not needed (CPU-only analysis) |
| **New Fields** | None | h_m1_results_path, primary_alpha, secondary_cv_threshold |

---

## Validation Checklist

- [x] ONE format only (dataclass)
- [x] Field names verified from h-m1 actual code
- [x] Inherited Configuration section included
- [x] Default values from research
- [x] Subtask count within budget (0 subtasks - analysis-only)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] MECHANISM PoC: Single fixed config (no variations)

---

## Notes

**MECHANISM PoC Configuration:**
- Analysis-only hypothesis (0 subtask budget)
- Reuses h-m1 artifacts (360 files: initial_weights.pt, final_weights.pt, loss_history.npy)
- No training hyperparameters needed
- No device configuration (CPU-only statistical analysis)
- Statistical thresholds from Phase 2C success criteria

**Non-Standard Values:**
- `h_m1_results_path=Path("../h-m1/results")`: Relative path assumes h-m2 and h-m1 are sibling directories

**Inherited from H-M1:**
- Seed count (30)
- Epoch count (10)
- Condition structure (4 conditions from 2 architectures × 2 datasets)

**Gate Criteria Mapping:**
- **Primary (MUST_WORK):** `primary_alpha=0.05` → All 4 conditions p < 0.05
- **Secondary (SHOULD):** `secondary_cv_threshold=1.0` → ≥2/4 conditions CV ≥ 1%

---

*Generated by Phase 3 Config Agent*
*Hypothesis: h-m2 (MECHANISM) | Gate: MUST_WORK*
*Next: Phase 4 Implementation (Task Execution)*
