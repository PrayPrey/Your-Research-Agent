# Config: H-M3
# Bidirectional Alignment Regression Verification

**Hypothesis ID:** H-M3
**Type:** MECHANISM (PoC — INCREMENTAL from H-M2)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Configuration inheritance pattern — extend H-M2 ExperimentConfig with H-M3 regression and bootstrap fields

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-M2)
**Status:** H-M2 config classes verified from actual code (`h-m2/code/src/config.py`)
**Config Files Found:** `h-m2/code/src/config.py`
**Pattern Used:** dataclass (same as H-M2)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-M2 Code)

```python
# From: docs/youra_research/h-m2/code/src/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    input_csv_path: str = "../../h-m1/results/h_m1_divergence_curve.csv"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    results_dir: str = "docs/youra_research/h-m2/results"
    results_filename: str = "h_m2_results.json"
    gap_csv: str = "h_m2_normalized_gap.csv"
    figure_dpi: int = 150
    high_kl_min_positive: int = 3
```

**Verified from:** `docs/youra_research/h-m2/code/src/config.py`

---

## A-2: Data Loader Config [Complexity: 1, Budget: 1]

Applied: Standard dataclass with YAML-loadable pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    # Input: H-M2 normalized gap CSV (feed-forward)
    input_csv_path: str = "docs/youra_research/h-m2/results/h_m2_normalized_gap.csv"

    # Required columns (validated on load)
    required_columns: tuple = ("kl_budget", "gap")
    min_n: int = 10  # minimum rows after NaN drop

    # Output directories
    figures_dir: str = "docs/youra_research/h-m3/figures"
    results_dir: str = "docs/youra_research/h-m3/results"
    results_filename: str = "h_m3_results.json"

    # Visualization
    figure_dpi: int = 150

    # Bootstrap
    n_boot: int = 10_000
    random_seed: int = 42

    # Gate thresholds (used in regression.py)
    slope_threshold: float = 0.0
    p_value_threshold: float = 0.05
    r_squared_threshold: float = 0.5

    def validate(self) -> None:
        import pandas as pd
        p = Path(self.input_csv_path)
        if not p.exists():
            raise FileNotFoundError(f"H-M2 feed-forward CSV not found: {p}")
        df = pd.read_csv(p)
        missing = [c for c in self.required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        df = df[list(self.required_columns)].dropna()
        assert len(df) >= self.min_n, f"Need >= {self.min_n} rows after NaN drop, got {len(df)}"

    @property
    def results_json_path(self) -> str:
        return str(Path(self.results_dir) / self.results_filename)


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    cfg = ExperimentConfig()
    cfg_path = Path(path)
    if cfg_path.exists():
        with open(cfg_path) as f:
            data = yaml.safe_load(f) or {}
        valid_keys = ExperimentConfig.__dataclass_fields__
        for k, v in data.items():
            if k in valid_keys:
                setattr(cfg, k, v)
    return cfg
```

### YAML Schema (`config.yaml`)

```yaml
# H-M3 Experiment Configuration

# Input: H-M2 normalized gap CSV (feed-forward)
input_csv_path: docs/youra_research/h-m2/results/h_m2_normalized_gap.csv

# Data validation
required_columns: ["kl_budget", "gap"]
min_n: 10

# Output
figures_dir:      docs/youra_research/h-m3/figures
results_dir:      docs/youra_research/h-m3/results
results_filename: h_m3_results.json

# Visualization
figure_dpi: 150

# Bootstrap
n_boot: 10000
random_seed: 42

# Gate thresholds (used in regression.py)
slope_threshold:     0.0   # OLS slope must exceed this
p_value_threshold:   0.05  # p-value must be below this
r_squared_threshold: 0.5   # R² must exceed this
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data loading configuration | csv_path default, required columns `["kl_budget", "gap"]`, `min_n=10` assertion, NaN check in `validate()` |

---

## Inherited Field Mapping

| Field | H-M2 Value | H-M3 Value | Change |
|-------|-----------|-----------|--------|
| `input_csv_path` | `h-m1/results/h_m1_divergence_curve.csv` | `h-m2/results/h_m2_normalized_gap.csv` | Updated (feed-forward from H-M2) |
| `figures_dir` | `h-m2/figures` | `h-m3/figures` | Updated |
| `results_dir` | `h-m2/results` | `h-m3/results` | Updated |
| `results_filename` | `h_m2_results.json` | `h_m3_results.json` | Updated |
| `figure_dpi` | 150 | 150 | Inherited |
| `random_seed` | — (not in H-M2 code) | 42 | **NEW** (bootstrap reproducibility) |
| `high_kl_min_positive` | 3 | — | **Dropped** (H-M2 gate not reused) |
| `gap_csv` | `h_m2_normalized_gap.csv` | — | **Dropped** (consumed as `input_csv_path`) |
| `required_columns` | — | `("kl_budget", "gap")` | **NEW** |
| `min_n` | — | 10 | **NEW** (data validation) |
| `n_boot` | — | 10_000 | **NEW** (bootstrap iterations) |
| `slope_threshold` | — | 0.0 | **NEW** (regression gate) |
| `p_value_threshold` | — | 0.05 | **NEW** (regression gate) |
| `r_squared_threshold` | — | 0.5 | **NEW** (regression gate) |
