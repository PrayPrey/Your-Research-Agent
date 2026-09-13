# Config: h-e1

**Applied**: inline-constants pattern (no tunable hyperparameters; all values fixed by Phase 2B)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict (inline constants in `run_experiment.py`)

---

## Study Type

This is a **statistical observational study**, not a training experiment. There are no tunable hyperparameters. All statistical thresholds are pre-defined by Phase 2B and must not be changed between runs (changing them would constitute p-hacking).

---

## Constants (Inline in `run_experiment.py`)

```python
# --- File Paths ---
CSV_PATH    = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR = 'docs/youra_research/h-e1/figures'
OUTPUT_PATH = 'docs/youra_research/h-e1/04_validation.md'

# --- Statistical Constants (fixed by Phase 2B — NOT tunable) ---
N_BOOTSTRAP  = 1000   # Bootstrap resamples; 1000 is standard for 95% CI stability
RANDOM_STATE = 42     # Reproducibility seed
ALPHA        = 0.05   # Conventional significance threshold
R_THRESHOLD  = 0.15   # Minimum |r_partial| effect size (pre-registered in Phase 2B)
VIF_WARN     = 5.0    # Multicollinearity warning (GVIF > 5 flags problematic collinearity)
N_MIN        = 200    # Minimum rows after NaN drop; assert-guarded in data_loader.py
```

---

## Dependencies (Pinned)

```
pandas>=2.0,<3
numpy>=1.24,<2
scipy>=1.11,<2
pingouin>=0.5.4,<1
statsmodels>=0.14,<1
matplotlib>=3.7,<4
seaborn>=0.13,<1
```

No training frameworks (torch, tensorflow, etc.) required.

---

## Notes

- No subtasks: config is 6 inline constants — no separate config module needed.
- No environment variables: paths are relative to project root, sufficient for single-machine runs.
- Do not vary `ALPHA`, `R_THRESHOLD`, or `VIF_WARN` between runs; these are pre-registered thresholds, not search parameters.
