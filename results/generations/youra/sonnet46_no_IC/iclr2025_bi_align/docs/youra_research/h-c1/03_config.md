# Configuration: h-c1 (Length-Controlled Win-Rate Quartile Analysis)

Applied: flat module-level constants pattern (verified from h-m3 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on h-m3)
**Status**: config patterns verified from base code (`h-m3/code/experiment_hm3.py`)
**Config Files Found**: `h-m3/code/experiment_hm3.py` — flat module-level constants, no dataclass, no config.py
**Pattern Used**: module-level constants — all prior hypotheses (h-e1, h-m1, h-m2, h-m3) use this; h-c1 follows suit

---

## Inherited Configuration (Base Hypothesis)

### Constants (From Actual h-m3 Code — Verified)

```python
# h-m3/code/experiment_hm3.py (actual field names, lines 25-37)
CSV_PATH        = Path("docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv")
N_BOOTSTRAP     = 1000
RANDOM_STATE    = 42
ALPHA           = 0.05
N_QUARTILES     = 4
QUARTILE_LABELS = ['Q1', 'Q2', 'Q3', 'Q4']
MIN_N_CLEAN     = 200
MIN_GROUP_SIZE  = 5
QUARTILE_PALETTE = ['#d73027', '#fc8d59', '#91bfdb', '#4575b4']
FIGURE_SIZE_DEFAULT = (10, 6)   # from h-m3 config spec
FIGURE_SIZE_HEATMAP = (12, 8)
DPI             = 150
FIGURE_FORMAT   = 'png'
```

**Verified from**: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_bi_align/docs/youra_research/h-m3/code/experiment_hm3.py`

---

## H-C1 Configuration Changes

| Field | h-m3 value | h-c1 value | Reason |
|-------|-----------|-----------|--------|
| `FIGURES_DIR` | `h-m3/figures` | `h-c1/figures` | Output dir change |
| `OUTPUT_PATH` | `h-m3/04_validation.md` | `h-c1/04_validation.md` | Output dir change |
| `RESULTS_PATH` | `h-m3/experiment_results.json` | `h-c1/experiment_results.json` | Output dir change |
| `DEPENDENT_VAR` | `'delta'` | `'length_controlled_winrate'` | New DV: LC win-rate directly (not delta) |
| `GATE_KW_P` | single gate `kw_p < 0.05` | same | Unchanged |
| `GATE_DUNN_Q1_Q4_P` | not present | `dunn_q1_q4_p < 0.05` | Additional gate: both must pass |
| `HYPOTHESIS_ID` | `'h-m3'` | `'h-c1'` | Identity |

Unchanged: `N_BOOTSTRAP`, `RANDOM_STATE`, `ALPHA`, `N_QUARTILES`, `QUARTILE_LABELS`, `MIN_N_CLEAN`, `MIN_GROUP_SIZE`, `QUARTILE_PALETTE`, figure size/DPI/format constants.

---

## A-1: Experiment Constants [Complexity: 1, Budget: 0]

### Configuration (module-level constants in experiment_hc1.py)

```python
from pathlib import Path

# --- Identity ---
HYPOTHESIS_ID = 'h-c1'

# --- Paths ---
CSV_PATH     = Path("docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv")
FIGURES_DIR  = Path("docs/youra_research/h-c1/figures")
OUTPUT_PATH  = Path("docs/youra_research/h-c1/04_validation.md")
RESULTS_PATH = Path("docs/youra_research/h-c1/experiment_results.json")

# --- Statistical ---
N_BOOTSTRAP    = 1000
RANDOM_STATE   = 42
ALPHA          = 0.05
MIN_N_CLEAN    = 200
MIN_GROUP_SIZE = 5

# --- Gate conditions (BOTH must pass) ---
# Non-standard: dual gate — kw_p tests global effect, dunn_q1_q4_p tests Q1 vs Q4 specifically
GATE_KW_P        = ALPHA          # Kruskal-Wallis omnibus p < 0.05
GATE_DUNN_Q1_Q4  = ALPHA          # Dunn post-hoc Q1 vs Q4 Bonferroni-adjusted p < 0.05

# --- Column mapping ---
DEPENDENT_VAR    = 'length_controlled_winrate'   # DV: LC win-rate (not delta)
GROUPING_VAR     = 'win_rate'                    # quartile grouping based on raw win_rate
DELTA_COL        = 'delta'                       # still computed but not primary DV

# --- Quartile grouping ---
N_QUARTILES      = 4
QUARTILE_LABELS  = ['Q1', 'Q2', 'Q3', 'Q4']
QUARTILE_PALETTE = ['#d73027', '#fc8d59', '#91bfdb', '#4575b4']

# --- Visualization ---
FIGURE_SIZE_DEFAULT = (10, 6)
FIGURE_SIZE_HEATMAP = (12, 8)
DPI           = 150
FIGURE_FORMAT = 'png'
FIGURE_NAMES  = {
    'boxplot': 'fig1_lc_winrate_boxplot.png',
    'scatter': 'fig2_scatter_winrate_lc_winrate.png',
    'heatmap': 'fig3_dunn_heatmap.png',
    'bar':     'fig4_quartile_median_bar.png',
}
```

### Subtasks [0/0 used]

No config-only subtasks — all constants live inline in `experiment_hc1.py`.

---

## Dependencies (Unchanged from h-m3)

```
# docs/youra_research/h-c1/requirements.txt
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
statsmodels>=0.13.0
matplotlib>=3.5.0
seaborn>=0.12.0
scikit-posthocs>=0.7.0
```

No new dependencies vs h-m3.

---

## Self-Validation

- [x] ONE format only (flat constants — no dataclass duplication)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (dual gate, DEPENDENT_VAR change)
- [x] Subtask count within budget (0/0)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names from h-m3 actual code
- [x] H-C1 Configuration Changes section included
