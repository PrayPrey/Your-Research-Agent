# Configuration: h-m2 (Temporal Prediction)

**Applied**: Statistical-regression-with-resampling config pattern (fixed seed, small-N bootstrap/LOO constants) — consistent with h-e1 flat-dict config style.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Config classes verified from base code — h-e1 uses a module-level `CONFIG` dict in `config.py`, not a dataclass. h-m2 follows the same flat-constants style (per 03_architecture.md), not a dataclass, to stay consistent with the reused `h-e1/code/config.py` import pattern.
**Config Files Found**: `h-e1/code/config.py` (flat `CONFIG` dict + `TARGET_BENCHMARKS`)
**Pattern Used**: Flat module-level constants (dict-like), matching h-e1

---

## Format: Hardcoded Constants (module-level, `h-m2/code/config.py`)

```python
# Temporal cutoff
CUTOFF_DATE: str = "2019-01-01"
MIN_HISTORY_YEARS_PRE_CUTOFF: int = 5
MIN_PRE_CUTOFF_ENTRIES: int = 10

# DNSI windowing (matches h-e1 default)
WINDOW_MONTHS: int = 6

# Regression / resampling
N_BOOTSTRAP: int = 10000
SEED: int = 1

# Gate thresholds
R2_PASS_THRESHOLD: float = 0.3
R2_FAIL_THRESHOLD: float = 0.1
LOO_R2_THRESHOLD: float = 0.1
CI_LOWER_INFORMATIONAL_THRESHOLD: float = 0.1

# Gap ground truth (from published papers, all 2019+)
GAP_GROUND_TRUTH: dict = {
    "ImageNet": {"gap": 0.125, "source": "Recht et al. 2019"},
    "CIFAR-10": {"gap": 0.04, "source": "Recht et al. 2019"},
    "CIFAR-100": {"gap": 0.05, "source": "Recht (scaled)"},
    "ObjectNet": {"gap": 0.425, "source": "Barbu et al. 2019"},
}

# ObjectNet reuses ImageNet's SOTA history for DNSI (tests ImageNet-trained models)
BENCHMARK_DNSI_SOURCE: dict = {
    "ImageNet": "ImageNet",
    "CIFAR-10": "CIFAR-10",
    "CIFAR-100": "CIFAR-100",
    "ObjectNet": "ImageNet",
}

# Output paths
FIGURES_DIR: str = "figures"
H_E1_CODE_DIR: str = "../../h-e1/code"
```

**Rationale for non-standard values:**
- `SEED = 1` (not 42): fixed per PRD/architecture spec for reproducible bootstrap.
- `N_BOOTSTRAP = 10000`: per FR-3.3, standard for small-N bootstrap CI stability.
- `MIN_PRE_CUTOFF_ENTRIES = 10`, `MIN_HISTORY_YEARS_PRE_CUTOFF = 5`: per FR-2.3, ensures DNSI computed on sufficiently long pre-cutoff windows.

---

## Inherited Configuration (Base Hypothesis: h-e1)

```python
# From: h-e1/code/config.py (ACTUAL CODE, verified via Serena)
# Imported directly at runtime via sys.path injection (H_E1_CODE_DIR), not copied:
from config import CONFIG, TARGET_BENCHMARKS   # h-e1/code/config.py
from data import load_data, extract_sota_history  # h-e1/code/data.py
from metrics import DNSIComputer, validate_dnsi   # h-e1/code/metrics.py
```

`DNSIComputer.compute_dnsi(sota_history, difficulty_proxy)` (h-e1) takes pre-parsed `list[tuple[datetime, float]]` — h-m2's `TemporalDNSIComputer` filters this list by `CUTOFF_DATE` before delegating to it. No h-e1 config fields are overridden; `WINDOW_MONTHS` mirrors h-e1's default of 6.

**Verified from**: `h-e1/code/` (actual implementation, per 03_architecture.md Codebase Analysis).

---

## Subtasks [4/4 used — B-1]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Cutoff + history constants | `CUTOFF_DATE`, `MIN_HISTORY_YEARS_PRE_CUTOFF`, `MIN_PRE_CUTOFF_ENTRIES`, `WINDOW_MONTHS` |
| C-1-2 | Bootstrap/seed constants | `N_BOOTSTRAP`, `SEED` |
| C-1-3 | Gate thresholds | `R2_PASS_THRESHOLD`, `R2_FAIL_THRESHOLD`, `LOO_R2_THRESHOLD`, `CI_LOWER_INFORMATIONAL_THRESHOLD` |
| C-1-4 | Gap ground truth + path constants | `GAP_GROUND_TRUTH`, `BENCHMARK_DNSI_SOURCE`, `FIGURES_DIR`, `H_E1_CODE_DIR` |
