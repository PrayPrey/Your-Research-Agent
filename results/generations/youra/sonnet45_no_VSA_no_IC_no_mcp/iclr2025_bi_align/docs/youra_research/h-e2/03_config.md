# Configuration Specification: h-e2

**Hypothesis:** AI response diversity correlates with query diversity (r > 0.4)
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-25

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Config pattern verified from h-e1
**Config Files Found:** `h-e1/code/config.py`
**Pattern Used:** dataclass (Python)

---

## Configuration Schema

Applied: Standard dataclass pattern from h-e1

```python
"""Experiment configuration for h-e2 diversity correlation analysis."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for query-response diversity correlation experiment."""
    
    # Dataset
    dataset_name: str = "Anthropic/hh-rlhf"
    split: str = "train"
    min_turns: int = 2
    
    # Diversity Metric
    ngram_size: int = 1  # distinct-1
    
    # Statistical Testing
    alpha: float = 0.05
    correlation_threshold: float = 0.4
    random_seed: int = 42
    
    # Output
    output_dir: str = "../results"
    figures_dir: str = "../figures"
    
    # Sampling (EXISTENCE = single run, no grid)
    max_samples: int = None  # Use full dataset


def get_config():
    """Get experiment configuration."""
    return ExperimentConfig()
```

---

## Parameter Rationale

| Parameter | Value | Reason |
|-----------|-------|--------|
| `min_turns` | 2 | Need 1 query + 1 response minimum |
| `ngram_size` | 1 | distinct-1 standard for diversity (Li et al., 2016) |
| `alpha` | 0.05 | Standard significance level |
| `correlation_threshold` | 0.4 | Success criterion from PRD |
| `random_seed` | 42 | Reproducibility |
| `max_samples` | None | Full dataset for EXISTENCE claim |

---

## Usage Example

```python
from config import get_config

config = get_config()
dataset = load_dataset(config.dataset_name, split=config.split)
# Filter: min_turns, compute distinct-n, test correlation
```

---

## Inherited Configuration

No base hypothesis. Green-field config design following h-e1 pattern for consistency.

---

## Validation

- [x] Single format (dataclass only)
- [x] No hyperparameter grid (EXISTENCE)
- [x] Default values from research
- [x] Ready for copy-paste to Phase 4
- [x] Consistent with h-e1 pattern
