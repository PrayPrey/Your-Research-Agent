# Configuration Design: H-M2 - G3 Superiority Over Minimal Feedback

**Date:** 2026-03-30
**Hypothesis Type:** MECHANISM (Post-hoc Statistical Analysis)
**Applied:** dataclass-config-pattern

---

## Inherited Configuration

### From H-M1 (Base Hypothesis)

| Config Field | H-M1 Value | H-M2 Usage |
|--------------|------------|------------|
| results_path | `h-m1/results/repair_results.json` | Input data source |
| n_cases | 304 | Expected paired samples |

---

## Configuration Dataclass

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Config:
    # Paths
    h_m1_results_path: str = "../h-m1/results/repair_results.json"
    results_dir: str = "results"
    figures_dir: str = "figures"
    
    # Statistical Thresholds
    difference_threshold: float = 0.10  # 10 percentage points
    alpha: float = 0.05
    
    # Target Conditions
    target_granularities: Tuple[str, str] = ("G0", "G3")
    expected_n_pairs: int = 304
    
    # Visualization
    figure_dpi: int = 150
    figure_size: Tuple[int, int] = (8, 6)
    colors: dict = field(default_factory=lambda: {
        "G0": "#2ecc71",
        "G3": "#e74c3c",
        "threshold": "#f39c12"
    })
```

---

## Gate Configuration

```python
@dataclass
class GateConfig:
    gate_type: str = "SHOULD_WORK"
    difference_threshold: float = 0.10
    alpha: float = 0.05
    expected_result: str = "FAIL"
```

---

## Subtasks

| ID | Task | Complexity |
|----|------|------------|
| A-5.1 | Visualization Configuration | 4 |

---

## Configuration Summary

| Category | Key Settings |
|----------|--------------|
| Paths | h-m1 results, output dirs |
| Thresholds | 10pp difference, alpha=0.05 |
| Data | G0 vs G3, 304 pairs |
| Gate | SHOULD_WORK, expected FAIL |

---

*Generated for Phase 3 Implementation Planning*
