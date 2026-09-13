# Configuration: h-m2 (Residual Capability Signal)

Applied: flat module-level constants pattern (verified from h-e1 and h-m1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on h-e1 and h-m1)
**Status**: config patterns verified from base code
**Config Files Found**: `h-e1/code/run_experiment.py`, `h-m1/code/run_experiment.py` (module-level constants, no dataclass)
**Pattern Used**: module-level constants dict — h-e1 and h-m1 both use flat module-level constants, not dataclasses

---

## Inherited Configuration (Base Hypothesis)

### Constants (From Actual Code — Verified)

```python
# h-e1/code/run_experiment.py (actual field names)
CSV_PATH     = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
N_BOOTSTRAP  = 1000
RANDOM_STATE = 42
ALPHA        = 0.05
N_MIN        = 200          # ← actual name in h-e1 (not MIN_N_CLEAN)

# h-m1/code/run_experiment.py (actual field names)
# CSV_PATH     same
# RANDOM_STATE same
# ALPHA        same
# N_MIN        same (not MIN_N_CLEAN)
# VIF_THRESHOLD = 5.0  (h-m1 uses VIF_THRESHOLD, h-e1 uses VIF_WARN)
```

**Verified from**: `docs/youra_research/h-e1/code/run_experiment.py` and `docs/youra_research/h-m1/code/run_experiment.py`

**Name mapping note**: PRD spec uses `MIN_N_CLEAN` — actual base code uses `N_MIN`. h-m2 uses `MIN_N_CLEAN` for clarity (new file, no import compatibility needed).

---

## A-8: Configuration Schemas [Complexity: 1, Budget: 2]

Applied: flat module-level constants pattern (matches h-e1/h-m1 convention)

### C-8-1: ExperimentConfig

```python
# docs/youra_research/h-m2/code/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class ExperimentConfig:
    # Paths
    csv_path: str    = "docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv"
    figures_dir: str = "docs/youra_research/h-m2/figures/"
    output_path: str = "docs/youra_research/h-m2/04_validation.md"

    # Statistical constants (pre-defined by Phase 2B — not tunable)
    n_bootstrap: int   = 1000
    random_state: int  = 42
    alpha: float       = 0.05
    min_n_clean: int   = 200

    # FWL consistency check (non-standard: h-m2-specific targets)
    h_e1_r_partial: float = 0.9851   # target from h-e1 result
    fwl_tolerance: float  = 0.02     # max |ρ_residual - h_e1_r_partial|

CFG = ExperimentConfig()
```

Usage in `run_experiment.py`:
```python
from config import CFG

df = load_and_validate(CFG.csv_path)
bootstrap_partial_corr(df, CFG.n_bootstrap, CFG.random_state)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | ExperimentConfig dataclass | Frozen dataclass with all constants; singleton `CFG` instance |
| C-8-2 | Requirements specification | requirements.txt with pinned versions |

---

## C-8-2: Environment / Dependency Specification

```
# docs/youra_research/h-m2/requirements.txt
pandas>=1.5.0
numpy>=1.22.0
scipy>=1.9.0
statsmodels>=0.13.0
pingouin>=0.5.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

Pinned exact versions for reproducibility (install with `pip install -r requirements.txt`):
```
# docs/youra_research/h-m2/requirements-lock.txt
pandas==2.2.2
numpy==1.26.4
scipy==1.13.1
statsmodels==0.14.2
pingouin==0.5.4
matplotlib==3.9.0
seaborn==0.13.2
```

The lock file is optional — the `>=` spec in requirements.txt is sufficient for PoC. Use lock file only if exact reproducibility across machines is required.

---

## Self-Validation

- [x] ONE format only (dataclass — no dict duplication)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (h_e1_r_partial, fwl_tolerance)
- [x] Subtask count within budget (2/2)
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names
- [x] Field names verified from actual base code (N_MIN vs MIN_N_CLEAN discrepancy noted)
