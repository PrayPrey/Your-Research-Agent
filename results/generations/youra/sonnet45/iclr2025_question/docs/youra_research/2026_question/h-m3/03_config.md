# Configuration Specification: h-m3 Bootstrap CI Stability

**Date:** 2026-03-21
**Hypothesis ID:** h-m3 (MECHANISM - Analysis-Only)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)

Applied: Statistical analysis modular pattern, Bootstrap resampling standard

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 actual code
**Config Files Found:** `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-e1/code/config.py`
**Pattern Used:** dataclass (simple flat config class)

Verified actual field names and defaults from h-e1 implementation. Base hypothesis uses flat dataclass with `datasets`, `architectures`, `seeds`, `epochs`, `lr`, `momentum`, `batch_size`, `data_root`, `results_dir`, `figures_dir`.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from base hypothesis:

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    batch_size: int = 64
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False
    data_root: str = "./data"
    results_dir: str = "./results"
    figures_dir: str = "./figures"
```

**Verified from**: h-e1/code/config.py (actual implementation)

---

## A-1: Configuration Setup [Complexity: 4, Budget: 1]

Applied: Flat dataclass pattern (matching h-e1 base)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M3 Bootstrap CI Stability Analysis."""

from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class BootstrapConfig:
    """Configuration for bootstrap variance CI analysis."""

    # Bootstrap parameters
    n_resamples: int = 1000
    confidence_level: float = 0.95
    ci_width_threshold_pct: float = 50.0
    random_seed: int = 42

    # Data loading (from h-e1 artifacts)
    h_e1_results_path: str = "../../h-e1/code/results/experiment_logs.csv"
    conditions: List[str] = field(default_factory=lambda: [
        "1layer_mnist",
        "1layer_fashion_mnist",
        "2layer_mnist",
        "2layer_fashion_mnist"
    ])

    # Output paths
    results_dir: str = "./results"
    figures_dir: str = "./figures"

    # Visualization settings
    dpi: int = 300
    figsize_distributions: tuple = (12, 10)
    figsize_ci_width: tuple = (10, 6)
    figsize_scatter: tuple = (10, 6)

    def __post_init__(self):
        """Ensure directories exist."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Bootstrap Config | Bootstrap parameters (B=1000, CI=95%, threshold=50%), paths, visualization settings |

---

## A-2: Data Loading from h-e1 [Complexity: 8, Budget: 1]

Applied: CSV parsing with pandas (standard pattern)

### Configuration (Module-Level Constants)

```python
"""Data loading configuration for h-e1 test accuracy extraction."""

# Expected data format
EXPECTED_COLUMNS = ["dataset", "architecture", "seed", "test_accuracy", "device", "error"]
EXPECTED_SAMPLES_PER_CONDITION = 30
VALID_DATASETS = ["mnist", "fashion_mnist"]
VALID_ARCHITECTURES = ["1layer", "2layer"]

# Data validation
ACCURACY_MIN = 0.0
ACCURACY_MAX = 100.0
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data Loading Config | CSV column names, validation constraints, condition mapping |

---

## A-3: Bootstrap Core Algorithm [Complexity: 12, Budget: 1]

Applied: NumPy bootstrap resampling (percentile method)

### Configuration (Algorithm Parameters)

```python
"""Bootstrap algorithm configuration."""

BOOTSTRAP_CONFIG = {
    "resample_method": "choice_with_replacement",
    "variance_ddof": 1,
    "percentile_method": "linear",
    "ci_lower_percentile": 2.5,
    "ci_upper_percentile": 97.5
}
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Algorithm Config | Resampling method, variance estimator (ddof=1), percentile bounds |

---

## Configuration Values Summary

### Bootstrap Parameters
- **Resamples (B):** 1000 (standard from literature)
- **Confidence Level:** 95% (α=0.05)
- **CI Method:** Percentile [2.5, 97.5]
- **Variance Estimator:** Sample variance with ddof=1 (Bessel's correction)
- **Random Seed:** 42 (reproducibility)

### Gate Validation
- **CI Width Threshold:** ≤ 50% of point estimate
- **Gate Type:** SHOULD_WORK
- **Failure Action:** Add N sensitivity analysis to exploration phase

### Data Loading
- **Source:** h-e1/code/results/experiment_logs.csv
- **Expected Format:** CSV with 120 rows (4 conditions × 30 seeds)
- **Columns:** dataset, architecture, seed, test_accuracy, device, error
- **Validation:** Check 30 samples per condition, no NaN/Inf, range [0, 100]

### Conditions
1. **1layer_mnist** - 1-layer MLP on MNIST (30 samples)
2. **1layer_fashion_mnist** - 1-layer MLP on Fashion-MNIST (30 samples)
3. **2layer_mnist** - 2-layer MLP on MNIST (30 samples)
4. **2layer_fashion_mnist** - 2-layer MLP on Fashion-MNIST (30 samples)

### Visualization
- **DPI:** 300 (publication quality)
- **Format:** PNG
- **Figures:**
  - bootstrap_distributions.png (4 subplots, 12×10 inches)
  - ci_width_comparison.png (bar chart, 10×6 inches)
  - variance_vs_ci_width.png (scatter plot, 10×6 inches)

### Outputs
- **Results Directory:** ./results/
  - bootstrap_results.json
  - gate_result.json
- **Figures Directory:** ./figures/
  - bootstrap_distributions.png
  - ci_width_comparison.png
  - variance_vs_ci_width.png

---

## Usage Example

```python
from config import BootstrapConfig

# Use default configuration
config = BootstrapConfig()

# Access bootstrap parameters
print(f"Bootstrap resamples: {config.n_resamples}")
print(f"CI level: {config.confidence_level}")
print(f"Threshold: {config.ci_width_threshold_pct}%")

# Access paths
print(f"Loading data from: {config.h_e1_results_path}")
print(f"Saving results to: {config.results_dir}")

# Iterate over conditions
for condition in config.conditions:
    print(f"Processing: {condition}")

# Customize for testing
test_config = BootstrapConfig(
    n_resamples=100,  # Faster for testing
    h_e1_results_path="./test_data/experiment_logs.csv"
)
```

---

## Validation Checklist

- [x] ONE format only (dataclass - matches h-e1 base pattern)
- [x] Field names verified from actual base config
- [x] Default values from research (B=1000 standard, CI=95% standard)
- [x] Bootstrap parameters complete (resamples, CI, threshold, seed)
- [x] Data loading paths match h-e1 outputs
- [x] Visualization settings included (DPI, figsize)
- [x] Subtask count within budget (3/3)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included

---

## Notes

**MECHANISM Analysis Configuration:**
- Pure statistical analysis (no training hyperparameters)
- Bootstrap resampling parameters from literature standards
- Data loading reuses h-e1 experiment_logs.csv
- CPU-only execution (<30 seconds runtime)

**Standard Values (No Rationale Needed):**
- B=1000: Bootstrap literature standard
- CI=95%: Statistical convention
- ddof=1: Unbiased variance estimator
- Random seed=42: Reproducibility standard

**Non-Standard Values:**
- CI width threshold=50%: Rajput 2023 criterion for stable estimation

**Differences from h-e1 Config:**
- No training hyperparameters (lr, momentum, epochs, batch_size)
- No determinism settings (cudnn, cublas) - not needed for CPU analysis
- No GPU settings (CUDA_VISIBLE_DEVICES) - CPU-only
- Added bootstrap-specific parameters (n_resamples, confidence_level)
- Simplified paths (no data_root, only results_dir/figures_dir)

---

**Configuration Complexity:** LOW (Analysis-Only, No Training)
**Total Subtasks:** 3/3 used
**Next Phase:** Phase 4 (Analysis Code Implementation)
