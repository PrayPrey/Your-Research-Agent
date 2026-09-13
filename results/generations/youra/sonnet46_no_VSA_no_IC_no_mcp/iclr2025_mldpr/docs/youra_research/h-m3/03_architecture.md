# Architecture: H-M3

**Applied**: Standard scipy parameter extraction pattern (pcov → perr → CI95)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/run.py`
**Findings**: Single-file H-M2 experiment. `fit_logistic()` returns `{popt, pcov, ci95, converged}`. `load_timeseries()` reads `months`/`monthly_max` CSV. H-M3 imports these directly; adds extraction + validation layer on top.

---

## Design Decision

H-M3 is a **standalone** `h-m3/code/run.py` that imports reusable functions from H-M2 via sys.path injection. Rationale: H-M2 must remain unmodified (it is a validated PASS experiment); H-M3 adds the extraction/validation layer separately.

---

## File Organization

- `h-m3/code/run.py` — main experiment script (single file, all H-M3 logic)
- `h-m3/figures/` — 4 output figures
- `h-m3/results.json` — serialized results
- `h-m3/experiment.log` — run log

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| `logistic` | `from run_hm2 import logistic` (via sys.path) | `h-m2/code/run.py` |
| `fit_logistic` | `from run_hm2 import fit_logistic` | `h-m2/code/run.py` |
| `load_timeseries` | `from run_hm2 import load_timeseries` | `h-m2/code/run.py` |
| `_r2_aic` | `from run_hm2 import _r2_aic` | `h-m2/code/run.py` |

**Verified from**: `docs/youra_research/h-m2/code/run.py` (actual implementation)

**Import pattern** (sys.path injection at top of h-m3/code/run.py):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m2" / "code"))
import run as run_hm2  # noqa: E402
```

---

## Modules

### ParameterExtractor (`h-m3/code/run.py` — inline functions)

**Dependencies**: `fit_logistic` (H-M2), `numpy`

```python
RELEASE_OFFSETS = {"glue": 0, "superglue": 0}  # t=0 is already benchmark release in H-M2 data

def extract_params(popt: np.ndarray, pcov: np.ndarray,
                   benchmark: str) -> dict: ...
# Returns: {K, r, t0_relative, t0_absolute, perr, ci95, pcov_finite}

def bootstrap_ci(t: np.ndarray, y: np.ndarray,
                 n_resamples: int = 500) -> np.ndarray: ...
# Returns: perr array shape (3,) — fallback when pcov diagonal contains inf
```

### PlausibilityGate (`h-m3/code/run.py` — inline functions)

**Dependencies**: `extract_params` output dict

```python
GATE_THRESHOLDS = {
    "K_lo": 0.85, "K_hi": 1.0,
    "t0_abs_lo": 6, "t0_abs_hi": 48,
    "ci_t0_width_max": 12.0,
}

def check_plausibility(params: dict) -> dict: ...
# Returns: {K_in_range, r_positive, t0_in_range, ci_t0_narrow, all_pass}

def verify_mechanism_activated(popt: np.ndarray, pcov: np.ndarray,
                                params: dict) -> tuple[bool, dict]: ...
# Returns: (all_ok: bool, indicators: dict)
```

### Visualization (`h-m3/code/run.py` — inline functions)

**Dependencies**: `matplotlib`, extracted params, timeseries data

```python
def plot_gate_metrics(params_by_bm: dict, out_dir: Path) -> None: ...
# FR-7.1: bar chart K/r/t0_absolute vs thresholds

def plot_param_ci(params_by_bm: dict, out_dir: Path) -> None: ...
# FR-7.2: error bars for K, r, t0 per benchmark

def plot_logistic_annotated(data: dict, fits: dict,
                             params_by_bm: dict, out_dir: Path) -> None: ...
# FR-7.3: scatter + curve annotated with K asymptote, t0 vertical line

def plot_t0_timeline(params_by_bm: dict, out_dir: Path) -> None: ...
# FR-7.4: calendar date timeline vs rapid-growth periods
```

### ResultsWriter (`h-m3/code/run.py` — inline function)

**Dependencies**: `json`

```python
def write_results(params_by_bm: dict, gate_by_bm: dict,
                  mechanism: dict, out_path: Path) -> None: ...
# Writes h-m3/results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup + H-M2 import | Create h-m3/code/run.py skeleton, sys.path injection, verify H-M2 imports work | 5 | 1+1+1+2 |
| A-2 | Data loading (reuse H-M2) | Call `load_timeseries` for GLUE + SuperGLUE; verify t=0 is benchmark release; document offset | 6 | 1+2+2+1 |
| A-3 | Parameter extraction layer | Implement `extract_params`: call `fit_logistic`, extract popt/pcov, compute perr/ci95, t0_absolute | 10 | 3+2+3+2 |
| A-4 | Bootstrap CI fallback | Implement `bootstrap_ci` (500 resamples, residual bootstrap); trigger when pcov diagonal has inf | 11 | 3+2+4+2 |
| A-5 | Plausibility gate checks | Implement `check_plausibility` and `verify_mechanism_activated`; apply to both benchmarks | 8 | 2+2+2+2 |
| A-6 | Visualization (4 figures) | Implement 4 plot functions (FR-7.1–7.4); save to h-m3/figures/ | 10 | 3+1+3+3 |
| A-7 | Results serialization + gate verdict | `write_results` to h-m3/results.json; print summary; sys.exit(0/1) | 5 | 1+1+1+2 |
| A-8 | t0 border case handling | If t0_absolute < 6, log justification, test relaxed [0,48] threshold, document in results | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-6], Low(4-8): [A-1, A-2, A-5, A-7, A-8]

---

## Data Flow

- `load_timeseries(csv_path)` → `(t, y)` arrays
- `fit_logistic(t, y)` → `{popt, pcov, ci95, converged}`
- `extract_params(popt, pcov, benchmark)` → params dict (with bootstrap fallback if pcov inf)
- `check_plausibility(params)` → gate flags dict
- `verify_mechanism_activated(popt, pcov, params)` → (bool, indicators)
- 4 plot functions → `h-m3/figures/*.png`
- `write_results(...)` → `h-m3/results.json`
- `sys.exit(0 if all_pass else 1)`
