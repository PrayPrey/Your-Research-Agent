# Configuration: h-m2 Shape Descriptor Differentiation

Applied: Standard dataclass pattern (no domain-specific KB patterns matched)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config class verified from actual code via direct file read
**Config Files Found**: `h-m1/code/config.py` (read directly)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260325_mldpr/h-m1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Data
    min_series_length: int = 12
    target_n_series: int = 500
    random_state: int = 42

    # PELT parameters
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    pelt_jump: int = 1         # jump=1 evaluates all positions

    # Penalty selection
    penalty_range: tuple = (1.0, 100.0)
    n_penalties: int = 20

    # Gate threshold
    detection_rate_threshold: float = 0.50

    # Output paths
    figures_dir: str = "h-m1/figures"
    output_path: str = "h-m1/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
```

**Verified from**: `docs/youra_research/20260325_mldpr/h-m1/code/config.py` (actual implementation)

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

Applied: Standard dataclass pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    # Data (consistent with h-e1/h-m1)
    n_clusters: int = 4
    n_series: int = 500
    random_state: int = 42

    # Shape descriptor parameters (reused from h-m1 methodology)
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3

    # Bootstrap parameters
    n_bootstrap: int = 100
    bootstrap_seed: int = 42

    # Gate threshold
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2

    # Output paths
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
    h_e1_cache_path: str = "../../h-e1/code/hf_dataset_cache.json"
    h_e1_model_path: str = "../../h-e1/code/kmeans_model.pkl"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config file | Write config.py with ExperimentConfig dataclass above |

---

## A-2: Data Loading [Complexity: 10, Budget: 1]

Applied: Standard dataclass pattern (no additional config needed)

No additional config fields required. DataLoader uses `ExperimentConfig` directly via `h_e1_cache_path` and `h_e1_model_path`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data paths | `h_e1_cache_path` and `h_e1_model_path` in ExperimentConfig cover all data loading paths |

---

## A-3: Shape Descriptor Analyzer [Complexity: 14, Budget: 1]

Applied: Standard scipy/ruptures defaults

Config fields in ExperimentConfig covering this module:
- `min_prominence: float = 0.1` - scipy.signal.find_peaks prominence threshold
- `pelt_model: str = "l2"` - ruptures PELT cost model
- `pelt_min_size: int = 3` - minimum segment size for PELT

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Descriptor params | `min_prominence`, `pelt_model`, `pelt_min_size` in ExperimentConfig |

---

## A-5: Variance Analysis [Complexity: 15, Budget: 1]

Applied: Standard bootstrap defaults (n=100, seed=42 from statistical best practices)

Config fields in ExperimentConfig covering this module:
- `n_bootstrap: int = 100` - bootstrap sample count
- `bootstrap_seed: int = 42` - reproducibility seed

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Bootstrap params | `n_bootstrap=100`, `bootstrap_seed=42` in ExperimentConfig |

---

## A-6: Gate Metrics [Complexity: 10, Budget: 1]

Applied: Standard threshold from Phase 2C specification

Config fields in ExperimentConfig covering this module:
- `variance_ratio_threshold: float = 2.0` - minimum ratio for passing descriptor
- `min_descriptors_passing: int = 2` - minimum count of passing descriptors for gate pass

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate thresholds | `variance_ratio_threshold=2.0`, `min_descriptors_passing=2` in ExperimentConfig |

---

## Full ExperimentConfig (Copy-Paste Ready)

```python
"""Configuration for h-m2 Shape Descriptor Differentiation experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for shape descriptor differentiation experiment."""

    # Data (consistent with h-e1/h-m1 for controlled comparison)
    n_clusters: int = 4
    n_series: int = 500
    random_state: int = 42

    # Shape descriptor parameters
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3

    # Bootstrap parameters
    n_bootstrap: int = 100
    bootstrap_seed: int = 42

    # Gate threshold
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2

    # Output paths (absolute paths overridden in main.py at runtime)
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
    h_e1_cache_path: str = "../../h-e1/code/hf_dataset_cache.json"
    h_e1_model_path: str = "../../h-e1/code/kmeans_model.pkl"
```
