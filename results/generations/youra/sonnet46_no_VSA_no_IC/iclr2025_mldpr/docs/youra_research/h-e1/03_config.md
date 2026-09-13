# Configuration: H-E1
# PELT Change-Point Detection on PwC Benchmark CoV Series

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: N/A — no domain-relevant Archon KB content found for statistical analysis domain

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (archive)
**Status**: existing patterns found via architecture doc (archive config.py uses module-level constants)
**Config Files Found**: `_archive/20260821T055106_routing_recovery/h-e1/code/config.py`
**Pattern Used**: module-level constants → upgraded to dataclass for IDE support and explicit typing

---

## C-5-1: config.py Full Dataclass + YAML Schema [Complexity: 3, Budget: 1 subtask]

**Applied**: Standard Python dataclass pattern (stdlib `dataclasses`)

### Configuration (Python Dataclass)

```python
# h-e1/code/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

# ponytail: global config singleton, no per-run config files needed for
# single-run statistical analysis; add YAML override support only if
# multi-condition sweeps are introduced.

_H1_DIR = Path(__file__).parent.parent  # h-e1/


@dataclass
class H1Config:
    # --- Data loading ---
    # MIN_PAPERS=5: archive used 10; PRD FR-1.4 sets default=5 to maximise N
    # while still excluding near-empty benchmarks.
    min_papers: int = 5
    # MIN_COV_ROWS=3: minimum rows for std(ddof=1) to be defined (need ≥2,
    # but 3 gives a more stable CoV estimate).
    min_cov_rows: int = 3

    # --- PELT algorithm ---
    # model="l2": L2 (least-squares) cost; appropriate for continuous
    # unimodal residuals. Gaussian assumption is reasonable for detrended CoV.
    pelt_model: str = "l2"
    # min_size=3: matches MIN_COV_ROWS; prevents degenerate 1- or 2-point
    # segments that cannot compute meaningful statistics.
    pelt_min_size: int = 3
    # jump=1: no subsampling; N=111 is small enough for exact search.
    pelt_jump: int = 1
    # pen_range=(1, 50): sensitivity sweep bounds. BIC penalty for N=111
    # and typical sigma~0.3 is ~sigma²*log(111)≈0.3²*4.7≈0.42; upper
    # bound of 50 is intentionally loose to show elbow structure.
    pen_range: tuple[float, float] = field(default_factory=lambda: (1.0, 50.0))
    # n_pen=20: 20 log-spaced values give sufficient resolution for elbow plot.
    n_pen: int = 20

    # --- Statistical tests ---
    # N_PERMUTATIONS=1000: standard for permutation tests; gives p-value
    # resolution of 0.001, sufficient for 0.05 gate.
    n_permutations: int = 1000
    # N_BOOTSTRAP=1000: matches permutation count; 95% CI from percentile
    # method is stable at 1000 resamples for N=111.
    n_bootstrap: int = 1000
    # SEED=42: canonical reproducibility seed; fixed per NFR-1.1.
    seed: int = 42

    # --- Gate thresholds ---
    # P_THRESHOLD=0.05: standard frequentist significance level (FR-4.5).
    p_threshold: float = 0.05
    # PAPER_COUNT_STAR_MIN=10: plausible minimum "mature benchmark" paper
    # count; below 10 the regime label is not scientifically meaningful.
    paper_count_star_min: int = 10
    # PAPER_COUNT_STAR_MAX=120: near-maximum observed paper_count in PwC
    # data (~111 benchmarks, max paper_count ≈ 130); 120 caps detection
    # before data boundary where PELT segments would be trivially small.
    paper_count_star_max: int = 120
    # BOOTSTRAP_CI_WIDTH_MAX=20: reliability criterion (FR-5.4); a CI
    # spanning > 20 papers is too wide to be actionable for downstream
    # hypotheses H-M1/M2/M3.
    bootstrap_ci_width_max: int = 20

    # --- Output paths (absolute, resolved at import time) ---
    figures_dir: str = field(
        default_factory=lambda: str(_H1_DIR / "figures")
    )
    results_json: str = field(
        default_factory=lambda: str(_H1_DIR / "experiment_results.json")
    )


# Module-level singleton — import this everywhere
CFG = H1Config()
```

### YAML Schema (`h-e1-config.yaml`) — Optional Override

The YAML file is **not required** for default runs. Place it at `h-e1/config.yaml`
to override any field; `run_experiment.py` checks for it and merges if present.

```yaml
# h-e1/config.yaml  (optional — omit to use all dataclass defaults)
# Only specify fields you want to override.

# Data loading
min_papers: 5
min_cov_rows: 3

# PELT algorithm
pelt_model: "l2"
pelt_min_size: 3
pelt_jump: 1
pen_range: [1.0, 50.0]
n_pen: 20

# Statistical tests
n_permutations: 1000
n_bootstrap: 1000
seed: 42

# Gate thresholds
p_threshold: 0.05
paper_count_star_min: 10
paper_count_star_max: 120
bootstrap_ci_width_max: 20

# Paths (auto-derived from file location if omitted)
# figures_dir: "/absolute/path/to/h-e1/figures"
# results_json: "/absolute/path/to/h-e1/experiment_results.json"
```

YAML loading snippet for `run_experiment.py`:

```python
import yaml
from pathlib import Path
from config import H1Config, CFG

def load_config(yaml_path: Path | None = None) -> H1Config:
    if yaml_path is None:
        yaml_path = Path(__file__).parent.parent / "config.yaml"
    if not yaml_path.exists():
        return CFG  # use defaults
    with open(yaml_path) as f:
        overrides = yaml.safe_load(f) or {}
    # pen_range from YAML comes as list → convert to tuple
    if "pen_range" in overrides:
        overrides["pen_range"] = tuple(overrides["pen_range"])
    from dataclasses import replace
    return replace(CFG, **overrides)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | config.py dataclass + YAML schema | H1Config dataclass with all parameters, defaults, and optional YAML override loader |

---

## C-5-2: experiment_results.json Schema [Complexity: 2, Budget: 1 subtask]

**Applied**: Python `TypedDict` (stdlib `typing`) — no third-party schema library needed for single-output JSON.

### JSON Schema

```json
{
  "permutation_p": 0.023,
  "paper_count_star": 47.0,
  "bootstrap_ci_lower": 32.0,
  "bootstrap_ci_upper": 61.0,
  "bootstrap_ci_width": 29.0,
  "n_bkps_detected": 1,
  "piecewise_f_p": 0.011,
  "ols_rho": -0.28,
  "ols_r2": 0.078,
  "gate_passed": true,
  "gate_reason": "permutation_p=0.023 < 0.05 AND paper_count_star=47 in [10, 120]",
  "n_benchmarks": 111,
  "bic_penalty_used": 0.423,
  "breakpoint_idx": 34
}
```

**Field notes (non-obvious only):**
- `paper_count_star`: `null` when `n_bkps_detected == 0`
- `breakpoint_idx`: 0-based index into `sorted_paper_counts`; `null` when no breakpoint detected
- `gate_reason`: human-readable string explaining pass or fail condition; always populated
- `bic_penalty_used`: `sigma² * log(T)` computed from actual residuals; stored for reproducibility

### Python TypedDict Definition

```python
# In run_experiment.py (or a separate types.py if reused across modules)
from typing import TypedDict

class ExperimentResults(TypedDict):
    permutation_p: float
    paper_count_star: float | None      # None if no breakpoint detected
    bootstrap_ci_lower: float
    bootstrap_ci_upper: float
    bootstrap_ci_width: float
    n_bkps_detected: int
    piecewise_f_p: float
    ols_rho: float
    ols_r2: float
    gate_passed: bool
    gate_reason: str
    n_benchmarks: int
    bic_penalty_used: float
    breakpoint_idx: int | None          # None if no breakpoint detected
```

### json.dump Snippet

```python
import json
from pathlib import Path

def save_results(results: ExperimentResults, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved → {path}")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-2 | experiment_results.json schema | TypedDict definition, JSON example, and json.dump snippet |

---

## Summary

| Task | Format | Key Params |
|------|--------|------------|
| C-5-1 | Python dataclass `H1Config` | 14 fields, all with defaults; YAML optional override |
| C-5-2 | `TypedDict ExperimentResults` | 14 fields; `paper_count_star` and `breakpoint_idx` nullable |
