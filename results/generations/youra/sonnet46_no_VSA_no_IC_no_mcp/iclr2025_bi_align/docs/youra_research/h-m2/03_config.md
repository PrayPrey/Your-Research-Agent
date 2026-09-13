# Config: H-M2
# Calibration-Alignment Divergence Gap Verification

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC — INCREMENTAL from H-M1)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Configuration inheritance pattern — extend H-M1 ExperimentConfig with H-M2-specific gate thresholds

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-M1)
**Status:** H-M1 config classes verified from actual code (`h-m1/code/src/config.py`)
**Config Files Found:** `h-m1/code/src/config.py`
**Pattern Used:** dataclass (same as H-M1)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-M1 Code)

```python
# From: docs/youra_research/h-m1/code/src/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    coste_csv_path: str = "data/coste_digitized.csv"
    gao_csv_path: str = "data/gao_digitized.csv"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    results_dir: str = "docs/youra_research/h-m1/results"
    results_filename: str = "h_m1_results.json"
    divergence_csv: str = "h_m1_divergence_curve.csv"
    min_kl_levels: int = 5
    monotonicity_rho_threshold: float = 0.8
    p_value_threshold: float = 0.05
    peak_kl_min: float = 1.0
    peak_kl_max: float = 9.0
    divergence_min: float = 0.0
    figure_dpi: int = 150
    random_seed: int = 1
```

**Verified from:** `docs/youra_research/h-m1/code/src/config.py`

---

## ExperimentConfig: H-M2

Applied: Configuration object pattern — single dataclass, YAML-loadable, validate-on-entry

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    # Input: H-M1 divergence curve CSV (feed-forward)
    input_csv_path: str = "docs/youra_research/h-m1/results/h_m1_divergence_curve.csv"

    # Output directories
    figures_dir: str = "docs/youra_research/h-m2/figures"
    results_dir: str = "docs/youra_research/h-m2/results"
    results_filename: str = "h_m2_results.json"
    gap_csv: str = "h_m2_gap_curve.csv"

    # Gate thresholds
    high_kl_min_positive: int = 3      # n_positive_high_kl >= this (FR-4.1)
    rho_gap_kl_min: float = 0.0        # rho_gap_kl must exceed this (FR-4.2)

    # Visualization
    figure_dpi: int = 150              # inherited from H-M1

    # Reproducibility
    random_seed: int = 1               # inherited from H-M1

    def validate(self) -> None:
        """Raise FileNotFoundError if H-M1 input CSV is missing."""
        p = Path(self.input_csv_path)
        if not p.exists():
            raise FileNotFoundError(f"H-M1 feed-forward CSV not found: {p}")

    @property
    def results_json_path(self) -> str:
        return str(Path(self.results_dir) / self.results_filename)

    @property
    def gap_csv_path(self) -> str:
        return str(Path(self.results_dir) / self.gap_csv)


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return ExperimentConfig()
    with open(cfg_path) as f:
        data = yaml.safe_load(f) or {}
    valid_keys = ExperimentConfig.__dataclass_fields__
    return ExperimentConfig(**{k: v for k, v in data.items() if k in valid_keys})
```

### YAML Schema (`config.yaml`)

```yaml
# H-M2 Experiment Configuration

# Input: H-M1 divergence curve (feed-forward)
input_csv_path: docs/youra_research/h-m1/results/h_m1_divergence_curve.csv

# Output
figures_dir:      docs/youra_research/h-m2/figures
results_dir:      docs/youra_research/h-m2/results
results_filename: h_m2_results.json
gap_csv:          h_m2_gap_curve.csv

# Gate thresholds
high_kl_min_positive: 3    # FR-4.1: gap positive at >= N high-KL levels
rho_gap_kl_min:       0.0  # FR-4.2: Spearman rho(kl, gap) must exceed this

# Visualization
figure_dpi: 150

# Reproducibility
random_seed: 1
```

### Inherited Field Mapping

| Field | H-M1 Value | H-M2 Value | Change |
|-------|-----------|-----------|--------|
| `figure_dpi` | 150 | 150 | Inherited |
| `random_seed` | 1 | 1 | Inherited |
| `divergence_csv` (output) | `h_m1_divergence_curve.csv` | — | Consumed as `input_csv_path` |
| `input_csv_path` | — | `h-m1/results/h_m1_divergence_curve.csv` | **NEW** (feed-forward from H-M1) |
| `gap_csv` | — | `h_m2_gap_curve.csv` | **NEW** |
| `high_kl_min_positive` | — | 3 | **NEW** (FR-4.1 gate) |
| `rho_gap_kl_min` | — | 0.0 | **NEW** (FR-4.2 gate) |
| `coste_csv_path`, `gao_csv_path` | set | — | **Dropped** (H-M2 reads H-M1 output, not raw data) |
| `min_kl_levels`, thresholds | set | — | **Dropped** (H-M1 gates not reused) |
