# Configuration: h-m1 PELT Changepoint Detection

**Hypothesis:** PELT Changepoint Detection for HuggingFace Dataset Download Trajectories
**Type:** MECHANISM (PoC)
**Gate:** MUST_WORK (detection_rate > 0.50)

Applied: minimal-poc-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (direct file read of h-e1/code/config.py)
**Config Files Found**: `docs/youra_research/20260325_mldpr/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260325_mldpr/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Data collection
    min_downloads: int = 100
    min_months: int = 12
    target_n_datasets: int = 500

    # Clustering
    k_range: tuple = (3, 8)
    max_iter: int = 10
    n_init: int = 2
    random_state: int = 42

    # Bootstrap stability
    n_bootstrap: int = 100
    bootstrap_ratio: float = 0.8

    # Evaluation thresholds (gate criteria)
    silhouette_threshold: float = 0.25
    jaccard_threshold: float = 0.65

    # Output paths
    figures_dir: str = "h-e1/figures"
    output_path: str = "h-e1/04_validation.md"
```

**Verified from**: `docs/youra_research/20260325_mldpr/h-e1/code/config.py` (actual implementation)

**Key field names verified** (h-m1 uses different names from h-e1):
- h-e1 uses `target_n_datasets`; h-m1 uses `target_n_series` (different domain)
- h-e1 uses `min_months`; h-m1 uses `min_series_length`
- `random_state: int = 42` carried over unchanged

---

## A-1: Setup & Config [Complexity: 5, Budget: 2 subtasks]

**Applied**: minimal-poc-pattern (single dataclass, EXISTENCE rules)

### Configuration (Python Dataclass)

```python
"""Configuration for h-m1 PELT Changepoint Detection experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for PELT changepoint detection experiment."""

    # Data (consistent with h-e1 for controlled comparison)
    min_series_length: int = 12
    target_n_series: int = 500
    random_state: int = 42

    # PELT parameters
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    # Non-standard: jump=1 evaluates all positions (ruptures default=5); needed for short series (min=12)
    pelt_jump: int = 1

    # Penalty selection (CROPS-style BIC grid search)
    penalty_range: tuple = (1.0, 100.0)
    # Non-standard: 20 log-spaced values per CROPS methodology (Haynes et al. 2017)
    n_penalties: int = 20

    # Gate threshold
    detection_rate_threshold: float = 0.50

    # Output paths (absolute paths overridden in main.py at runtime)
    figures_dir: str = "h-m1/figures"
    output_path: str = "h-m1/04_validation.md"
    cache_path: str = "../h-e1/code/hf_dataset_cache.json"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config dataclass | Implement `ExperimentConfig` in `h-m1/code/config.py` |
| C-1-2 | Requirements file | Create `h-m1/code/requirements.txt` with ruptures>=1.1.0, numpy, pandas, matplotlib, seaborn, huggingface_hub |
