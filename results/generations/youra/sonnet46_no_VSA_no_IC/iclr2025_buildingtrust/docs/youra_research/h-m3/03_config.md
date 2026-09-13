# Config: H-M3
# Per-Pair Adversarial Rank Disruption Analysis

Applied: flat module-level constants pattern (mirroring h-m1/h-m2 config.py style)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-M2)
**Status**: config classes verified from base code (h-m2)
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: module-level constants (no dataclass — matches h-m1/h-m2 style)

---

## Inherited Configuration (Base Hypothesis)

From actual `h-m2/code/config.py` (verified):

```python
# H-M2 field names → H-M3 status
DELTA_RHO_GATE: float = 0.2      # NOT inherited — h-m3 uses per-pair RHO_THRESHOLD instead
FISHER_Z_P_THRESHOLD: float = 0.10  # NOT inherited — h-m3 uses ALPHA = 0.05
N_COMMON_MIN: int = 8            # NOT inherited — h-m3 raises to 10 (per task spec)
RANDOM_SEED: int = 1             # NOT inherited — h-m3 uses 42 (per task spec)
H_M1_DATA_DIR: Path              # Pattern inherited — h-m3 adds H_M2_DATA_DIR
```

**H-M3 changes from H-M2:**
- Gate changes from `delta_rho >= 0.2` to per-pair `(rho < 0.4 OR p >= 0.05)` for both pairs
- `N_COMMON_MIN` raised back to 10 (h-m3 uses h-m2 CSV with cleaner coverage)
- `RANDOM_SEED` set to 42 (project-wide standard per task spec)
- `ALPHA` set to 0.05 (stricter than h-m2's 0.10 — mechanism-level confirmation)
- Adds `RANK_REVERSAL_MIN_SHIFT`, `RHO_FAIRNESS_HM1`, `N_BOOTSTRAP`
- Adds `H_M2_DATA_DIR` cross-reference; retains `H_M1_RESULTS` for rho_fairness baseline

---

## A-1: Config & Scaffolding [Complexity: 5, Budget: 1 subtask]

**Applied**: flat module-level constants pattern

### Configuration (Python — `code/config.py`)

```python
"""H-M3 configuration: per-pair adversarial rank disruption analysis.

Extends H-M2. Reads trustllm_scores_hm2.csv (already contains all required columns).
H-M1 results.json consulted only for rho_fairness baseline reference value.
"""
from pathlib import Path

# --- Gate thresholds ---
RHO_THRESHOLD: float = 0.4       # per-pair partial Spearman gate (both pairs must be below)
ALPHA: float = 0.05              # significance level for Fisher z one-tailed test

# --- Analysis parameters ---
RANDOM_SEED: int = 42
N_BOOTSTRAP: int = 1000
N_COMMON_MIN: int = 10           # minimum models for valid partial correlation (N-3 >= 7 DOF)
RANK_REVERSAL_MIN_SHIFT: int = 5  # non-standard: 5 rank positions = "substantive" reversal threshold

# --- H-M1 reference value (loaded at runtime) ---
# Used for bar chart baseline comparison only; not in gate logic.
# Fallback 0.60 if h-m1/results/results.json is missing.
RHO_FAIRNESS_HM1_FALLBACK: float = 0.60

# --- Paths ---
_HERE = Path(__file__).parent.parent
FIGURES_DIR = _HERE / "figures"
RESULTS_JSON = _HERE / "results.json"

# Cross-hypothesis data sources
H_M2_DATA_DIR = _HERE.parent / "h-m2" / "data"      # trustllm_scores_hm2.csv lives here
H_M1_RESULTS  = _HERE.parent / "h-m1" / "results" / "results.json"  # rho_fairness source
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write config.py | Thresholds, paths, H_M2_DATA_DIR, RHO_FAIRNESS_HM1_FALLBACK |

---

## A-8/A-9: Visualizations [Complexity: 19, Budget: 1 subtask]

**Applied**: flat module-level constants pattern; color palette extended from H-M2

### Figure Configuration

```python
# Visualization defaults — embed in code/visualize.py
FIG_DPI: int = 150

PALETTE: dict = {
    "fairness":  "#4C72B0",   # blue  — rho_fairness bar / reference line
    "advglue":   "#DD8452",   # orange — AdvGLUE pair
    "anli":      "#55A868",   # green  — ANLI pair
    "threshold": "#8C8C8C",   # grey   — rho=0.4 dashed threshold line
    "reversal":  "#C44E52",   # red    — highlight large rank shifts
    "neutral":   "#CCB974",   # tan    — neutral / small shift
}

FIG_SPECS: dict = {
    "gate_metrics_comparison": {
        "figsize": (7, 5),
        "ylabel": "Partial Spearman rho (MMLU-controlled)",
        "threshold_line": 0.4,
        "show_ci": True,           # 95% CI error bars from bootstrap
    },
    "rank_scatter_advglue": {
        "figsize": (6, 6),
        "xlabel": "GLUE rank",
        "ylabel": "AdvGLUE rank",
        "color_by": "rank_shift_abs",   # |rank_GLUE - rank_AdvGLUE|
        "cmap": "RdYlGn_r",
        "annotate_models": True,
    },
    "rank_scatter_anli": {
        "figsize": (6, 6),
        "xlabel": "ANLI_R1 rank",
        "ylabel": "ANLI_R3 rank",
        "color_by": "rank_shift_abs",
        "cmap": "RdYlGn_r",
        "annotate_models": True,
    },
    "rank_reversal_heatmap": {
        "figsize": (10, 7),
        "cmap": "RdYlGn_r",
        "annot": True,
        "highlight_threshold": 5,  # cells where shift >= RANK_REVERSAL_MIN_SHIFT get border
        "sort_by": "glue_score",   # rows sorted by GLUE rank ascending
    },
    "correlation_summary_table": {
        "figsize": (9, 4),
        "rows": ["rho_fairness", "rho_advglue", "rho_anli"],
        "columns": ["rho", "ci_lower", "ci_upper", "p_asymptotic", "z_fisher", "p_fisher"],
        "fontsize": 11,
    },
    "fisher_z_distribution": {
        "figsize": (8, 5),
        "xlabel": "z (Fisher-transformed rho)",
        "show_threshold_z": True,   # vertical line at arctanh(0.4) = 0.424
        "annotate_pairs": True,     # label z_advglue and z_anli positions
    },
}
```

### Figure Configuration Table

| Figure | File | figsize | DPI | Format |
|--------|------|---------|-----|--------|
| gate_metrics_comparison | gate_metrics_comparison.png | (7, 5) | 150 | PNG |
| rank_scatter_advglue | rank_scatter_advglue.png | (6, 6) | 150 | PNG |
| rank_scatter_anli | rank_scatter_anli.png | (6, 6) | 150 | PNG |
| rank_reversal_heatmap | rank_reversal_heatmap.png | (10, 7) | 150 | PNG |
| correlation_summary_table | correlation_summary_table.png | (9, 4) | 150 | PNG |
| fisher_z_distribution | fisher_z_distribution.png | (8, 5) | 150 | PNG |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-89-1 | Visualization constants | FIG_DPI, PALETTE, FIG_SPECS for all 6 figures |

---

## YAML Schema: results.json Output

```yaml
# h-m3/results.json schema
type: object
properties:
  n_models:
    type: integer
    description: "Number of models in final DataFrame after NaN drop"
  advglue_pair:
    type: object
    properties:
      rho:       {type: number}
      p_asymptotic: {type: number}
      ci_lower:  {type: number}
      ci_upper:  {type: number}
      z_fisher:  {type: number}
      p_fisher:  {type: number}
      significant: {type: boolean}
      reversals: {type: integer}
  anli_pair:
    type: object
    properties:
      rho:       {type: number}
      p_asymptotic: {type: number}
      ci_lower:  {type: number}
      ci_upper:  {type: number}
      z_fisher:  {type: number}
      p_fisher:  {type: number}
      significant: {type: boolean}
      reversals: {type: integer}
  gate_passed: {type: boolean}
  mechanism_ok: {type: boolean}
  mechanism_indicators:
    type: object
    properties:
      data_complete:    {type: boolean}
      n_sufficient:     {type: boolean}
      advglue_computed: {type: boolean}
      anli_computed:    {type: boolean}
      pairs_differ:     {type: boolean}
      reversals_counted:{type: boolean}
  rho_fairness_hm1: {type: number, description: "From h-m1/results/results.json or fallback 0.60"}
  seed: {type: integer, const: 42}
required: [n_models, advglue_pair, anli_pair, gate_passed, mechanism_ok, mechanism_indicators, rho_fairness_hm1, seed]
```

---

## Environment Spec (requirements.txt)

```
pingouin>=0.5.0
scipy>=1.10
numpy>=1.24
pandas>=1.5
matplotlib>=3.7
seaborn>=0.12
```
