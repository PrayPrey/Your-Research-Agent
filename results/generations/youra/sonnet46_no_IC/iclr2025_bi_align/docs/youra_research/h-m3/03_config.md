# Configuration: h-m3 (Quartile Monotonicity of Win-Rate Delta)

Applied: flat module-level constants pattern (verified from h-m2 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on h-m2)
**Status**: config patterns verified from base code (`h-m2/code/run_experiment.py`)
**Config Files Found**: `h-m2/code/run_experiment.py` — flat module-level constants, no dataclass, no config.py
**Pattern Used**: module-level constants — all prior hypotheses (h-e1, h-m1, h-m2) use this; h-m3 follows suit

---

## Inherited Configuration (Base Hypothesis)

### Constants (From Actual h-m2 Code — Verified)

```python
# h-m2/code/run_experiment.py (actual field names, line 8-14)
CSV_PATH     = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR  = 'docs/youra_research/h-m2/figures'
OUTPUT_PATH  = 'docs/youra_research/h-m2/04_validation.md'
N_BOOTSTRAP  = 1000
RANDOM_STATE = 42
ALPHA        = 0.05
H_E1_R_PARTIAL = 0.9851   # h-m2-specific, not inherited by h-m3
```

**Verified from**: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_bi_align/docs/youra_research/h-m2/code/run_experiment.py`

---

## A-1: Experiment Constants [Complexity: 1, Budget: 2]

Applied: flat module-level constants pattern (matches h-m2 convention)

### Configuration (module-level constants in experiment_hm3.py)

```python
# --- Paths ---
CSV_PATH     = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR  = 'docs/youra_research/h-m3/figures'
OUTPUT_PATH  = 'docs/youra_research/h-m3/04_validation.md'

# --- Statistical ---
N_BOOTSTRAP   = 1000
RANDOM_STATE  = 42
ALPHA         = 0.05
MIN_N_CLEAN   = 200
MIN_GROUP_SIZE = 5

# --- Quartile grouping ---
N_QUARTILES     = 4
QUARTILE_LABELS = ['Q1', 'Q2', 'Q3', 'Q4']

# --- Visualization ---
FIGURE_SIZE_DEFAULT = (10, 6)
FIGURE_SIZE_HEATMAP = (12, 8)
DPI                 = 150
FIGURE_FORMAT       = 'png'
FIGURE_NAMES = {
    'boxplot':    'fig1_delta_boxplot.png',
    'scatter':    'fig2_scatter_winrate_delta.png',
    'heatmap':    'fig3_dunn_heatmap.png',
    'bar':        'fig4_quartile_median_bar.png',
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Experiment constants | All constants in experiment_hm3.py as module-level vars |
| C-1-2 | Requirements specification | requirements.txt adding scikit-posthocs vs h-m2 |

---

## C-1-2: Environment / Dependency Specification

```
# docs/youra_research/h-m3/requirements.txt
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
statsmodels>=0.13.0
matplotlib>=3.5.0
seaborn>=0.12.0
scikit-posthocs>=0.7.0
```

New vs h-m2: `scikit-posthocs>=0.7.0` (for `posthoc_dunn` with Bonferroni correction). pingouin dropped — not needed for Kruskal-Wallis / Dunn workflow.

---

## Self-Validation

- [x] ONE format only (flat constants — no dataclass duplication)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (FIGURE_NAMES dict, MIN_GROUP_SIZE)
- [x] Subtask count within budget (2/2)
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names from h-m2 actual code
