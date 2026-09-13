# H-M2 Configuration

Contract richness stratification analysis — no LLM inference, no hyperparameter tuning.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: H-M1 actual code verified — no config.py exists; H-M1 uses module-level constants in `run_experiment.py`
**Config Files Found**: None in `h-m1/code/` — pattern is module-level constants
**Pattern Used**: module-level constants (matching H-M1 actual code pattern)

---

Applied: module-level constants pattern (from H-M1 `run_experiment.py` actual code)

---

## Inherited Configuration (Base Hypothesis)

H-M1 does not have a dedicated config.py. Constants are defined inline in `run_experiment.py`:

```python
# From: h-m1/code/run_experiment.py (ACTUAL CODE — verified)
CODE_DIR = Path(__file__).parent
ROOT = CODE_DIR.parent
RESULTS_DIR = str(ROOT / "code" / "results")   # ← h-m1/code/results/
FIGURES_DIR = str(ROOT / "figures")
N_WORKERS = 8
TIMEOUT_PER_INPUT = 5
SEED = 42
```

H-M1 per-task gap file: `h-m1/code/results/per_task_oracle_gap.json`
(verified from `statistical_analysis.save_results` path convention)

---

## A-1 through A-6: Path & Statistical Constants

**Applied**: Standard Python stdlib defaults (no non-standard values)

```python
# h-m2/code/config.py
from pathlib import Path

# --- Paths (resolved at import time) ---
CODE_DIR = Path(__file__).parent
ROOT = CODE_DIR.parent.parent          # h-m2/
H1_GAP_PATH = ROOT.parent / "h-m1" / "code" / "results" / "per_task_oracle_gap.json"
CONTRACTEVAL_PATH = ROOT.parent.parent.parent / "_archive" / "ContractEval" / "ContractEval.jsonl"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"

# --- Dataset ---
N_TASKS = 364

# --- Richness scoring weights ---
QUANTIFIER_WEIGHT = 3    # score += 3 * has_quantifier
RELATIONAL_WEIGHT = 2    # score += 2 * has_relational

# --- Statistical analysis ---
SEED = 42
N_BOOTSTRAP = 10_000     # bootstrap iterations for CI on rho
N_RESAMPLES = 9999       # permutation test resamples (odd: avoids tie with observed)

# --- Success threshold ---
SPEARMAN_THRESHOLD = 0.30
FLAT_GRADIENT_THRESHOLD = 0.15   # if rho < 0.15, flag FLAT_GRADIENT

# --- Output filenames ---
RESULTS_JSON = "h_m2_results.json"
RICHNESS_CSV = "richness_scores.csv"
```

### Subtasks [0/0 used — A-1 through A-6 have no config subtasks]

---

## A-7: Visualization Config [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard matplotlib defaults

```python
# h-m2/code/config.py (continued)

# --- Visualization ---
FIGURE_DPI = 150
FIGURE_SIZE_DEFAULT = (8, 6)    # (width, height) in inches
FIGURE_SIZE_WIDE = (10, 6)      # for heatmap

# Tier color palette (1=simple → 4=compound, blue-to-red gradient)
TIER_COLORS = {
    1: "#4393c3",   # blue  — simple
    2: "#92c5de",   # light blue — structural
    3: "#f4a582",   # light orange — relational
    4: "#d6604d",   # red — compound
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Figure layout constants | `FIGURE_DPI`, `FIGURE_SIZE_DEFAULT`, `FIGURE_SIZE_WIDE` — used by all 5 plot functions |
| C-7-2 | Tier color palette | `TIER_COLORS` dict (4 entries) — used by scatter, boxplot, violin plots |

---

## Notes for Phase 4

- `H1_GAP_PATH` must be confirmed at runtime — print path and check existence; raise `FileNotFoundError("Run H-M1 first")` if missing.
- `CONTRACTEVAL_PATH` is a best-guess based on H-M1 `data_loader.py` pattern; Phase 4 should make it overridable via `os.environ.get("CONTRACTEVAL_PATH", str(CONTRACTEVAL_PATH))`.
- All constants live in `h-m2/code/config.py`; each module imports only what it needs.
