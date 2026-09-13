# Configuration: h-m3 Archetype Recovery via Shape Descriptor Alignment

**Applied**: pipeline-dataclass-config-pattern (consistent with h-m2/h-e1 pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual h-m2 and h-e1 code
**Config Files Found**: `h-m2/code/config.py`, `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m2/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    n_clusters: int = 4
    n_series: int = 500
    random_state: int = 42
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    n_bootstrap: int = 100
    bootstrap_seed: int = 42
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"

# From: h-e1/code/config.py (ACTUAL CODE - verified)
# h_e1_cache_path verified as "hf_dataset_cache.json" (NOT "dataset_cache.json" as PRD states)
```

**Verified from**: `h-m2/code/config.py` and `h-e1/code/config.py` actual implementation

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

**Applied**: pipeline-dataclass-config-pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ExperimentConfig:
    """Configuration for h-m3 archetype recovery experiment."""

    # Data
    n_clusters: int = 4
    n_archetypes: int = 5
    random_state: int = 42

    # Alignment gate
    alignment_threshold: float = 0.70
    min_archetypes_recovered: int = 3

    # Normalization ranges (from h-m2 observed values)
    norm_growth_ratio: Tuple[float, float] = (0.3, 0.6)
    norm_peak_timing: Tuple[float, float] = (0.0, 0.03)
    norm_changepoint_count: Tuple[float, float] = (0.0, 5.0)
    norm_derivative_variance: Tuple[float, float] = (0.1, 0.4)

    # Figure output
    figure_dpi: int = 300
    figure_format: str = "png"

    # Paths (overridden in main.py with absolute paths at runtime)
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"
    figures_dir: str = "h-m3/figures"
    output_path: str = "h-m3/04_validation.md"

    def get_norm_ranges(self) -> Dict[str, Tuple[float, float]]:
        return {
            "growth_ratio": self.norm_growth_ratio,
            "peak_timing": self.norm_peak_timing,
            "changepoint_count": self.norm_changepoint_count,
            "derivative_variance": self.norm_derivative_variance,
        }
```

### Archetype Profiles Constant

```python
ARCHETYPE_PROFILES = {
    "sustained_growth": {
        "growth_ratio": 0.8,
        "peak_timing": 0.9,
        "changepoint_count": 0.2,
        "derivative_variance": 0.2,
    },
    "flash_in_pan": {
        "growth_ratio": 0.3,
        "peak_timing": 0.2,
        "changepoint_count": 0.8,
        "derivative_variance": 0.8,
    },
    "plateau": {
        "growth_ratio": 0.5,
        "peak_timing": 0.5,
        "changepoint_count": 0.2,
        "derivative_variance": 0.1,
    },
    "slow_burn": {
        "growth_ratio": 0.7,
        "peak_timing": 0.8,
        "changepoint_count": 0.1,
        "derivative_variance": 0.2,
    },
    "revival": {
        "growth_ratio": 0.4,
        "peak_timing": 0.6,
        "changepoint_count": 0.6,
        "derivative_variance": 0.5,
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | config.py with dataclass, norm_ranges, ARCHETYPE_PROFILES constant, path defaults |

---

## A-2 through A-11: Remaining Tasks

All tasks (A-2 through A-11) consume the remaining budget allocation. They share the single `ExperimentConfig` dataclass defined in A-1. No additional config classes are required.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data path validation | Validate h_e1_cache_path exists at runtime in main.py |
| C-2-2 | Norm ranges accessor | get_norm_ranges() returns dict for normalize_profile() in model.py |
| C-2-3 | Absolute path override pattern | main.py __main__ block sets absolute paths (mirrors h-m2 pattern) |

---

## Runtime Configuration (main.py pattern)

```python
# Mirrors h-m2/code/main.py absolute path override pattern (verified from actual code)
if __name__ == "__main__":
    base_dir = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr"
    config = ExperimentConfig(
        h_e1_cache_path=os.path.join(base_dir, "h-e1/code/hf_dataset_cache.json"),
        figures_dir=os.path.join(base_dir, "h-m3/figures"),
        output_path=os.path.join(base_dir, "h-m3/04_validation.md"),
    )
```

---

## Key Values Rationale (Non-Standard Only)

- `norm_peak_timing: (0.0, 0.03)` - h-m2 observed range for peak_timing is very narrow (0-0.03), not 0-1
- `norm_changepoint_count: (0.0, 5.0)` - h-m2 observed max ~5 changepoints per series
- `norm_derivative_variance: (0.1, 0.4)` - h-m2 observed range, not full 0-1 scale
- `alignment_threshold: 0.70` - from Phase 2C specification (non-negotiable gate parameter)
- `min_archetypes_recovered: 3` - SHOULD_WORK gate criterion from Phase 2C specification
