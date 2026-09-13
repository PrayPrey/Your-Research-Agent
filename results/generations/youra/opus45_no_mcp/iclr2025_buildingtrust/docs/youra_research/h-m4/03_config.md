# Configuration Design: H-M4

**Hypothesis:** Hedging-Confidence Correlation Analysis
**Date:** 2026-08-19

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: H-M3 config pattern reviewed (docs/youra_research/h-m3/03_config.md) - dataclass pattern reused for consistency; no shared config module to import (each hypothesis is self-contained)
**Config Files Found**: h-m3/03_config.md (spec reference only, no code/ dir present for h-m3 in this workspace)
**Pattern Used**: dataclass

Applied: minimal_config_pattern

---

## Configuration Schema

H-M4 is pure statistical analysis on cached H-M2 data (no training, no model inference). Single flat dataclass, no YAML duplication needed.

```python
# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class H_M4_Config:
    """Configuration for H-M4 hedging-confidence correlation analysis."""

    # Data paths
    h_m2_results_path: str = "../h-m2/code/results/h-m2_results.json"
    output_dir: str = "results"
    figures_dir: str = "figures"

    # Analysis settings
    min_samples: int = 500
    alpha: float = 0.05  # significance level

    # Gate thresholds
    correlation_threshold: float = -0.2

    # Visualization
    figure_dpi: int = 300
    figure_format: str = "png"

    # Hedging buckets for box plot
    hedging_buckets: List[str] = field(default_factory=lambda: ["0", "1-2", "3-5", "6+"])
```

---

## Default Values

| Parameter | Default | Notes |
|-----------|---------|-------|
| h_m2_results_path | `../h-m2/code/results/h-m2_results.json` | PRD-specified source |
| min_samples | 500 | Gate requirement (PRD 6.1) |
| alpha | 0.05 | Standard significance level |
| correlation_threshold | -0.2 | Gate condition (PRD 6.1) |
| figure_dpi | 300 | Higher than H-M3 (150) for paper-quality figures per PRD FR-5 |
| hedging_buckets | `["0","1-2","3-5","6+"]` | PRD FR-4 box plot spec |

---

*Configuration design for H-M4 correlation analysis - no training hyperparameters required*
