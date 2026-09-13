# Config: H-M2
# Differential Rank Stability — Fairness vs. Adversarial Robustness

Applied: flat module-level constants pattern (mirroring h-m1 config.py)
Applied: Standard Python module-level constants (no neural hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (h-m1)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: module-level constants dict (no dataclass — matches h-m1 style)

---

## Inherited Configuration (Base Hypothesis)

From actual `h-m1/code/config.py`:

```python
# h-m1 field names (verified from actual code)
GATE_RHO: float = 0.4          # not reused in h-m2 (different gate metric)
GATE_P: float = 0.05           # not reused
N_COMMON_MIN: int = 10         # h-m2 uses 8 (more permissive, robustness data sparser)
RANDOM_SEED: int = 1           # inherited unchanged
ALTERNATIVE: str = "greater"   # not reused (h-m2 uses two-sided)

# Paths pattern (inherited verbatim):
_HERE = Path(__file__).parent.parent
DATA_DIR   = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"
```

**H-M2 changes from h-m1:**
- Gate changes from `(rho >= GATE_RHO) & (p <= GATE_P)` to `delta_rho >= DELTA_RHO_GATE`
- `N_COMMON_MIN` lowered to 8 (robustness benchmark overlap is smaller)
- Adds `H_M1_DATA_DIR` for cross-hypothesis CSV loading
- Adds `ROBUSTNESS_SCORES` dict (same pattern as h-m1 `WINOGRANDE_SCORES`)

---

## A-1: Config & Scaffolding [Complexity: 5, Budget: 1 subtask]

**Applied**: module-level constants, same Path pattern as h-m1

### Configuration (Python — `code/config.py`)

```python
"""H-M2 configuration: gate thresholds, paths, robustness score constants."""
from pathlib import Path

# Gate thresholds
DELTA_RHO_GATE: float = 0.2          # primary gate: fairness partial rho minus mean robustness partial rho
FISHER_Z_P_THRESHOLD: float = 0.10   # lenient/exploratory (not 0.05 — mechanism-tier PoC)
N_COMMON_MIN: int = 8                # non-standard: 8 not 10 — robustness benchmarks cover fewer models

# Analysis parameters
RANDOM_SEED: int = 1

# Paths (same pattern as h-m1)
_HERE = Path(__file__).parent.parent
DATA_DIR    = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"

# Cross-hypothesis: load h-m1 validated CSV
H_M1_DATA_DIR = _HERE.parent / "h-m1" / "data"

# Robustness scores — TrustLLM benchmark suite
# Source: TrustLLM paper Table 2 (GLUE, AdvGLUE++, ANLI)
# Placeholder 0.0 values to be filled by Phase 4 from actual paper data
ROBUSTNESS_SCORES: dict = {
    # model_name: {glue_score, advglue_score, anli_r1_score, anli_r3_score}
    # All scores normalized to [0, 1]; higher = more robust
    "ChatGPT": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "GPT-4": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Llama2-7b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Llama2-13b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Llama2-70b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Vicuna-7b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Vicuna-13b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Vicuna-33b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "ChatGLM2": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Falcon": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Mistral-7b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Oasst-12b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "Alpaca-13b": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "ERNIE-3.5": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
    "PaLM2": {
        "glue_score": 0.0,
        "advglue_score": 0.0,
        "anli_r1_score": 0.0,
        "anli_r3_score": 0.0,
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write config.py | Paths, thresholds, ROBUSTNESS_SCORES dict |

---

## A-8: Visualizations [Complexity: 12, Budget: 2 subtasks]

**Applied**: matplotlib defaults matching h-m1 visualize.py style

### Configuration (embedded in `code/visualize.py`)

```python
# Visualization defaults
FIG_DPI = 150
PALETTE = {
    "fairness": "#4C72B0",   # blue
    "advglue":  "#DD8452",   # orange
    "anli":     "#55A868",   # green
    "delta":    "#C44E52",   # red — highlights the key differential
    "threshold": "#8C8C8C",  # grey dashed line for 0.2 gate
}

# Per-figure specs
FIG_SPECS = {
    "gate_metrics_comparison": {
        "figsize": (7, 5),
        "ylabel": "Partial Spearman rho (MMLU-controlled)",
        "threshold_line": 0.2,   # DELTA_RHO_GATE reference
        "show_ci": True,         # 95% CI error bars
    },
    "rank_heatmap": {
        "figsize": (10, 7),
        "cmap": "RdYlGn_r",      # red=high rank (worse), green=low rank (better)
        "annot": True,
        "sort_by": "mmlu",       # rows sorted by MMLU rank ascending
    },
    "per_dimension_scatter": {
        "figsize": (13, 4),      # 3-panel wide layout
        "panels": [
            {"x": "bbq_disambig", "y": "bbq_ambig",    "color": PALETTE["fairness"]},
            {"x": "glue_score",   "y": "advglue_score", "color": PALETTE["advglue"]},
            {"x": "anli_r1_score","y": "anli_r3_score", "color": PALETTE["anli"]},
        ],
        "annotate_rho": True,
    },
    "forest_plot": {
        "figsize": (8, 5),
        "rows": ["rho_fairness", "rho_advglue", "rho_anli", "delta_rho"],
        "threshold_line": 0.2,
        "ci_level": 0.95,
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Global viz defaults | FIG_DPI, PALETTE, shared style constants |
| C-8-2 | Per-figure specs | FIG_SPECS dict with figsize, axes labels, panel params for all 4 figures |

---

## YAML Schema: results.json Output

```yaml
# results/results.json schema
type: object
properties:
  n_models:
    type: integer
    description: "Number of models in final joined DataFrame"
  raw:
    type: object
    properties:
      rho_fair_raw: {type: number}
      rho_advglue_raw: {type: number}
      rho_anli_raw: {type: number}
      delta_rho_raw: {type: number}
  partial_mmlu:
    type: object
    properties:
      rho_fairness: {type: number}
      rho_fairness_p: {type: number}
      rho_fairness_ci95: {type: array, items: {type: number}, minItems: 2, maxItems: 2}
      rho_advglue: {type: number}
      rho_advglue_p: {type: number}
      rho_advglue_ci95: {type: array, items: {type: number}}
      rho_anli: {type: number}
      rho_anli_p: {type: number}
      rho_anli_ci95: {type: array, items: {type: number}}
      delta_rho: {type: number}
  fisher_z:
    type: object
    properties:
      z_stat: {type: number}
      p_value_two_tailed: {type: number}
  sensitivity_winogrande:
    type: object
    description: "Repeat of partial_mmlu with winogrande as covariate"
    properties:
      rho_fairness: {type: number}
      rho_advglue: {type: number}
      rho_anli: {type: number}
      delta_rho: {type: number}
      z_stat: {type: number}
      p_value_two_tailed: {type: number}
  gate:
    type: object
    properties:
      delta_rho_gate_threshold: {type: number, const: 0.2}
      gate_passed: {type: boolean}
      fisher_z_p_threshold: {type: number, const: 0.1}
      fisher_z_significant: {type: boolean}
  seed: {type: integer, const: 1}
required: [n_models, raw, partial_mmlu, fisher_z, sensitivity_winogrande, gate, seed]
```
