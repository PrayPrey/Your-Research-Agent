# Config: h-m1

**Applied**: inline-constants pattern (same as h-e1 — no tunable hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: config constants verified from h-e1 actual code (`run_experiment.py`)
**Config Files Found**: None — h-e1 uses inline constants, h-m1 follows same pattern
**Pattern Used**: hardcoded constants (inline in `run_experiment.py`)

---

## Inherited Configuration (Base Hypothesis)

### Constants (From Actual h-e1 Code)

```python
# From: docs/youra_research/h-e1/code/run_experiment.py (ACTUAL CODE)
CSV_PATH     = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
RANDOM_STATE = 42
ALPHA        = 0.05
VIF_WARN     = 5.0   # ← field name in h-e1 (renamed VIF_THRESHOLD in h-m1 for clarity)
N_MIN        = 200
```

Constants NOT inherited (h-e1 specific):
- `N_BOOTSTRAP = 1000` — bootstrap not used in h-m1 (OLS replaces bootstrap)
- `R_THRESHOLD = 0.15` — h-e1 partial-r gate; h-m1 uses OLS beta significance instead
- `FIGURES_DIR`, `OUTPUT_PATH` — h-m1 uses its own paths

---

## h-m1 Constants (Inline in `run_experiment.py`)

```python
# --- File Paths ---
CSV_PATH     = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR  = 'docs/youra_research/h-m1/figures/'
OUTPUT_PATH  = 'docs/youra_research/h-m1/04_validation.md'

# --- Statistical Constants (fixed by Phase 2B — NOT tunable) ---
RANDOM_STATE   = 42     # Reproducibility seed
ALPHA          = 0.05   # Conventional significance threshold
VIF_THRESHOLD  = 5.0    # Multicollinearity gate (VIF >= 5 triggers permutation fallback)
N_REPEATS      = 30     # Permutation importance resamples
N_MIN          = 200    # Minimum rows after NaN drop; assert-guarded in data_loader.py
```

---

## Experiment Metadata (YAML)

```yaml
hypothesis: h-m1
study_type: statistical_observational
method: OLS_regression
no_training: true
no_gpu: true
seed: 42
alpha: 0.05
vif_threshold: 5.0
n_repeats: 30
n_min: 200
data:
  source: AlpacaEval2_leaderboard
  path: docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
outputs:
  figures_dir: docs/youra_research/h-m1/figures/
  report: docs/youra_research/h-m1/04_validation.md
```

---

## Environment Setup

```
pandas>=2.0,<3
numpy>=1.24,<2
scipy>=1.11,<2
statsmodels>=0.14,<1
scikit-learn>=1.3,<2
matplotlib>=3.7,<4
seaborn>=0.13,<1
```

Install: `pip install pandas numpy scipy statsmodels scikit-learn matplotlib seaborn`

Additions vs h-e1: `scikit-learn` (for `LinearRegression` + `permutation_importance`).
Removed vs h-e1: `pingouin` (no partial Spearman needed).

---

## Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Constants block | Inline constants in `run_experiment.py` as shown above |
| C-2 | YAML metadata | Write `docs/youra_research/h-m1/experiment_meta.yaml` from schema above |
| C-3 | Requirements file | Write `docs/youra_research/h-m1/requirements.txt` with pinned ranges above |

---

## Notes

- Do not vary `ALPHA`, `VIF_THRESHOLD`, or `N_MIN` between runs — pre-registered thresholds, not search parameters.
- `N_REPEATS = 30` is the permutation fallback path only (VIF >= 5); for VIF < 5 path it is unused.
- No dataclass needed: 5 scalar constants + 3 paths; inline is simpler and matches h-e1 convention.
