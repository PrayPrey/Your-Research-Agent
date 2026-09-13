# Config: H-M1
# RLHF Proxy-Gold Divergence Mechanism Verification

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC — INCREMENTAL from H-E1)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Configuration inheritance pattern — extend H-E1 ExperimentConfig with H-M1-specific thresholds

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-E1)
**Status:** H-E1 config analyzed
**Config Files Found:** `h-e1/code/config.yaml` (YAML schema), `h-e1/code/src/config.py` (inferred from 03_config.md pattern)
**Pattern Used:** dataclass (same as H-E1)

**Inherited Configuration (Verified from H-E1 03_config.md):**
```python
# From h-e1/03_config.md ExperimentConfig — fields confirmed:
coste_csv_path: str       # "data/coste2023_kl_curves.csv"  → H-M1 uses "data/coste_digitized.csv"
gao_csv_path: str         # "data/gao2023_kl_curves.csv"    → H-M1 uses "data/gao_digitized.csv"
figures_dir: str          # "docs/youra_research/h-e1/figures" → H-M1: h-m1/figures
results_dir: str          # "docs/youra_research/h-e1/results" → H-M1: h-m1/results
min_kl_levels: int        # 5  (REUSE — same gate)
min_variation: float      # 0.01 (NOT reused — H-M1 uses different gate)
figure_dpi: int           # 150 (REUSE)
random_seed: int          # 1 (REUSE)
```

Note: H-M1 adds new threshold fields; min_variation is from H-E1 and not relevant here.
Note: Archon MCP unavailable (ablation mode). Patterns grounded from H-E1 config structure.

---

## C-E7-1: ExperimentConfig [Parent: E7, Complexity: 8, Budget: 1]

Applied: Configuration object pattern — centralize all tuneable values in H-M1 extension

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    # Input data (H-M1 naming; may symlink from H-E1)
    coste_csv_path: str = "data/coste_digitized.csv"
    gao_csv_path:   str = "data/gao_digitized.csv"

    # Output directories (H-M1 specific)
    figures_dir:      str = "docs/youra_research/h-m1/figures"
    results_dir:      str = "docs/youra_research/h-m1/results"
    results_filename: str = "h_m1_results.json"
    divergence_csv:   str = "h_m1_divergence_curve.csv"  # feed-forward to H-M2

    # Gate thresholds — H-M1 mechanism verification
    min_kl_levels:            int   = 5      # inherited from H-E1 spec
    monotonicity_rho_threshold: float = 0.8  # Spearman ρ(KL, RM) > 0.8 required
    p_value_threshold:          float = 0.05 # statistical significance
    peak_kl_min:                float = 1.0  # sanity: peak not at KL=0
    peak_kl_max:                float = 9.0  # sanity: peak within measurement range
    divergence_min:             float = 0.0  # sanity: RM > gold at final KL

    # Visualization
    figure_dpi: int = 150

    # Reproducibility
    random_seed: int = 1

    def validate(self) -> None:
        """Raise FileNotFoundError if required input CSV paths do not exist."""
        for attr in ("coste_csv_path",):  # primary only; Gao is secondary/optional
            p = Path(getattr(self, attr))
            if not p.exists():
                raise FileNotFoundError(f"Required input not found: {p}")

    @property
    def results_json_path(self) -> str:
        return str(Path(self.results_dir) / self.results_filename)

    @property
    def divergence_csv_path(self) -> str:
        return str(Path(self.results_dir) / self.divergence_csv)


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    """Load ExperimentConfig from YAML; fallback to defaults for missing keys."""
    cfg_path = Path(path)
    if not cfg_path.exists():
        return ExperimentConfig()
    with open(cfg_path) as f:
        data = yaml.safe_load(f) or {}
    return ExperimentConfig(**{k: v for k, v in data.items()
                               if k in ExperimentConfig.__dataclass_fields__})
```

### Equivalent YAML Schema (`config.yaml`)

```yaml
# H-M1 Experiment Configuration
# Extends H-E1 config pattern with mechanism-specific thresholds

# Input data
coste_csv_path: data/coste_digitized.csv
gao_csv_path:   data/gao_digitized.csv

# Output directories
figures_dir:      docs/youra_research/h-m1/figures
results_dir:      docs/youra_research/h-m1/results
results_filename: h_m1_results.json
divergence_csv:   h_m1_divergence_curve.csv

# Gate thresholds (H-M1 mechanism verification)
min_kl_levels:              5
monotonicity_rho_threshold: 0.8   # Spearman ρ(KL, RM) must exceed this
p_value_threshold:          0.05
peak_kl_min:                1.0   # nats; sanity bound
peak_kl_max:                9.0   # nats; sanity bound
divergence_min:             0.0   # RM − gold at final KL must exceed this

# Visualization
figure_dpi: 150

# Reproducibility
random_seed: 1
```

### Inherited Configuration Notes

| Field | H-E1 Value | H-M1 Value | Change |
|-------|-----------|-----------|--------|
| `coste_csv_path` | `data/coste2023_kl_curves.csv` | `data/coste_digitized.csv` | Renamed |
| `gao_csv_path` | `data/gao2023_kl_curves.csv` | `data/gao_digitized.csv` | Renamed |
| `min_kl_levels` | 5 | 5 | Inherited |
| `figure_dpi` | 150 | 150 | Inherited |
| `random_seed` | 1 | 1 | Inherited |
| `min_variation` | 0.01 | — | Dropped (different gate) |
| `monotonicity_rho_threshold` | — | 0.8 | **NEW** |
| `p_value_threshold` | — | 0.05 | **NEW** |
| `peak_kl_min/max` | — | 1.0 / 9.0 | **NEW** |
| `divergence_min` | — | 0.0 | **NEW** |
| `divergence_csv` | — | `h_m1_divergence_curve.csv` | **NEW** (feed-forward to H-M2) |

---

## C-E6-1: Reporter Configuration [Parent: E6, Complexity: 10, Budget: 2]

Applied: Result schema pattern — define required JSON fields for downstream consumers

### Results JSON Schema (`h_m1_results.json`)

```python
{
    # Required top-level fields (for H-M2 and hypothesis-loop gate check)
    "hypothesis_id":    "h-m1",
    "gate_pass":        bool,           # True iff rho_rm_kl > 0.8 AND reversal_confirmed
    "dataset":          "Coste2023",
    "n_kl_levels":      int,            # number of paired KL observations used

    # Monotonicity test
    "rho_rm_kl":        float,          # Spearman ρ(KL, RM)
    "p_rho":            float,          # p-value

    # Peak-reversal detection
    "reversal_confirmed": bool,
    "peak_kl":          float,          # KL level at gold preference peak (nats)
    "peak_kl_valid":    bool,           # peak_kl in [1.0, 9.0]

    # Divergence (feed-forward to H-M2)
    "divergence_final": float,          # rm[-1] - gold[-1]
    "divergence_max":   float,          # max of divergence_curve

    # Baseline (KL=0 reference)
    "baseline_rm":      float,
    "baseline_gold":    float,

    # Diagnostic messages
    "mono_reason":      str,
    "peak_reason":      str,
    "div_reason":       str,

    # Metadata
    "timestamp":        str,            # ISO 8601
    "config_path":      str,
}
```

### Divergence Curve CSV Schema (`h_m1_divergence_curve.csv`)

| Column | dtype | Description |
|--------|-------|-------------|
| `kl_budget` | float | KL divergence level (nats) |
| `rm_score` | float | Proxy reward at that level |
| `gold_preference` | float | Human preference at that level |
| `divergence_gap` | float | `rm_score - gold_preference` |

**Purpose:** Direct feed-forward to H-M2 for divergence gap quantification and regression.

---

## Subtasks [3/3 used from config budget]

| ID | Parent Epic | Description |
|----|-------------|-------------|
| C-E7-1 | E7 (8) | ExperimentConfig dataclass + YAML schema + load_config + validate |
| C-E6-1 | E6 (10) | Results JSON schema + divergence CSV schema definition |
| C-E6-2 | E6 (10) | `load_config()` integration in main.py + config.yaml placement |
