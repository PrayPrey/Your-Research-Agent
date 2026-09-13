# Configuration Design: H-E1 Benchmark Data Validation

**Date:** 2026-07-12  
**Hypothesis:** h-e1 - Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each  
**Type:** EXISTENCE (PoC Validation)  
**Phase:** 3 - Configuration Design

**Applied:** Standard dataclass pattern for configuration management (Python stdlib)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation - designing new config schema  
**Config Files Found:** None - new config design  
**Pattern Used:** Dataclass (Python 3.7+ @dataclass decorator)

---

## Configuration Overview

This validation study requires two configuration classes:
1. **ValidationConfig**: API parameters, filtering criteria, statistical thresholds
2. **PlotConfig**: Visualization styling for 5 required figures

**Format:** Python dataclasses (type-safe, minimal boilerplate)  
**File:** `code/config.py`

---

## C-1: API & Validation Configuration (Complexity: 1, Budget: 1)

**Applied:** REST API configuration pattern with retry logic defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import List


@dataclass
class ValidationConfig:
    """Configuration for Papers with Code API collection and validation."""
    
    # API Settings
    api_base_url: str = "https://paperswithcode.com/api/v1/"
    rate_limit_seconds: float = 1.0
    request_timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    
    # Data Collection Filters
    task_filter: str = "classification"
    start_year: int = 2019
    end_year: int = 2024
    allowed_metrics: List[str] = None
    
    # Validation Thresholds
    min_benchmarks: int = 100
    min_results_per_benchmark: int = 5
    min_domain_count: int = 2
    target_median_results: int = 7
    
    # Statistical Analysis Parameters
    effect_size: float = 0.57
    alpha: float = 0.05
    power: float = 0.80
    
    # Output Paths
    output_dir: str = "."
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    figures_dir: str = "figures"
    logs_dir: str = "logs"
    
    def __post_init__(self):
        """Set default allowed_metrics if not provided."""
        if self.allowed_metrics is None:
            self.allowed_metrics = ["accuracy", "f1"]
```

**Rationale for non-standard values:**
- `effect_size=0.57`: Medium effect size from Phase 2B power analysis (Cohen's d)
- `min_results_per_benchmark=5`: Minimum reproductions needed for variance calculation
- `target_median_results=7`: Target for sufficient CV calculation in downstream H-M3

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ValidationConfig Implementation | Create dataclass with API, filtering, and statistical parameters |

---

## C-2: Plot Styling Configuration (Complexity: 1, Budget: 1)

**Applied:** Matplotlib/seaborn default styling with minimal customization

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Tuple


@dataclass
class PlotConfig:
    """Styling configuration for validation report figures."""
    
    # Figure Dimensions
    figure_size: Tuple[int, int] = (10, 6)
    dpi: int = 300
    
    # Color Palette
    pass_color: str = "#2ecc71"
    fail_color: str = "#e74c3c"
    neutral_color: str = "#3498db"
    
    # Font Settings
    title_fontsize: int = 14
    label_fontsize: int = 12
    tick_fontsize: int = 10
    
    # Style
    style: str = "seaborn-v0_8-darkgrid"
    
    # Output Format
    save_format: str = "png"
    bbox_inches: str = "tight"
```

**Rationale for non-standard values:**
- `dpi=300`: Publication-quality figures for validation report
- `style="seaborn-v0_8-darkgrid"`: Clear gridlines for quantitative comparison plots

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PlotConfig Implementation | Create dataclass with matplotlib styling parameters |

---

## Usage Example

```python
from config import ValidationConfig, PlotConfig

# Initialize with defaults
config = ValidationConfig()

# Override specific parameters
config_custom = ValidationConfig(
    rate_limit_seconds=0.5,
    min_benchmarks=150
)

# Plot configuration
plot_config = PlotConfig()
```

---

## Configuration File Structure

**File:** `code/config.py`

```python
"""Configuration module for H-E1 benchmark data validation study."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ValidationConfig:
    # ... (see C-1)
    pass


@dataclass
class PlotConfig:
    # ... (see C-2)
    pass


# Default instances for convenience
DEFAULT_VALIDATION_CONFIG = ValidationConfig()
DEFAULT_PLOT_CONFIG = PlotConfig()
```

---

## Environment Variables

None required. All configuration is hardcoded with sensible defaults.

---

## Self-Validation Checklist

- [x] ONE format only (Dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2 used)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project noted (Serena skip acceptable)
- [x] EXISTENCE template applied (minimal config, no hyperparameter grid)

---

**Next Phase:** Phase 4 - Code Implementation  
**Output File:** `/workspace/TEST_mldpr/docs/youra_research/h-e1/03_config.md`
