---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
phase: "Phase 3"
date: "2026-08-25"
---

# Architecture: H-M1 — Temporal Structure Analysis of GLUE/SuperGLUE Leaderboards

Applied: statistical-correlation-pipeline (load → validate → correlate → report → plot)

## Codebase Analysis (Serena)

**Project Type**: incremental (extends H-E1 data outputs)
**Status**: green-field code — H-E1 code folder not yet implemented; H-E1 architecture doc used as reference
**Analyzed Path**: docs/youra_research/h-e1/ (architecture doc only; no src/ or code/ to analyze)
**Findings**: H-E1 produces `data/glue_timeseries_clean.csv` and `data/superglue_timeseries_clean.csv`. H-M1 reads these CSVs directly. No shared code modules exist yet — new single-file implementation.

---

## File Organization

```
docs/youra_research/h-m1/
├── code/
│   ├── run.py           # single entry point: load → analyze → report → plot
│   └── requirements.txt
└── figures/
    ├── gate_metrics.png
    ├── score_trajectory.png
    ├── gain_rate.png
    └── pre_post_inflection.png
```

Data inputs (from H-E1, read-only):
```
data/
├── glue_timeseries_clean.csv
└── superglue_timeseries_clean.csv
```

Single-file approach — all logic in `run.py`. No packages, no classes needed.

---

## Module Structure

### run.py — top-level functions

**Dependencies**: pandas, numpy, scipy.stats, matplotlib

```python
# --- Data loading & validation ---
def load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]: ...
# Reads CSV, expects columns: months (int), monthly_max (float).
# Returns (times, scores) sorted by months.
# Raises FileNotFoundError if H-E1 output missing.
# Asserts: time_span >= 24 months, n_obs >= 20, score std > 0.001

# --- Gain rate computation ---
def compute_gains(times: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...
# Returns (gain_times, gains) where gains = np.diff(scores), gain_times = times[1:]

# --- Core temporal analysis ---
def test_temporal_signal(
    times: np.ndarray,
    scores: np.ndarray,
    gains: np.ndarray,
    gain_times: np.ndarray,
) -> dict: ...
# Returns:
#   rho_monotonic: float   — spearmanr(times, scores); target > 0.8
#   rho_decel: float       — spearmanr(gain_times, gains); target < -0.3
#   pre_post_ratio: float  — mean(gains[:N//2]) / mean(gains[N//2:]); expected > 1.0
#   pass: bool             — rho_monotonic > 0.8 AND rho_decel < -0.3

# --- Pre/post inflection analysis ---
def split_inflection(
    gains: np.ndarray,
    inflection_idx: int | None = None,
) -> tuple[np.ndarray, np.ndarray]: ...
# Returns (pre_gains, post_gains). inflection_idx defaults to len(gains)//2.

# --- Results reporting ---
def print_results_table(benchmark_results: dict[str, dict]) -> None: ...
# Prints aligned table to stdout: benchmark | rho_mono | rho_decel | pre_post_ratio | PASS/FAIL

def save_results_json(benchmark_results: dict[str, dict], out_path: str) -> None: ...
# Writes results.json with all metrics + pass/fail per benchmark + overall verdict

# --- Visualization ---
def plot_gate_metrics(benchmark_results: dict[str, dict], out_dir: str) -> None: ...
# Saves gate_metrics.png: grouped bar chart rho_mono + rho_decel per benchmark
# with threshold lines at 0.8 and -0.3

def plot_score_trajectory(
    benchmark_id: str,
    times: np.ndarray,
    scores: np.ndarray,
    out_dir: str,
) -> None: ...
# Saves score_trajectory.png: line plot monthly_max vs months for GLUE + SuperGLUE

def plot_gain_rate(
    benchmark_id: str,
    gain_times: np.ndarray,
    gains: np.ndarray,
    out_dir: str,
) -> None: ...
# Saves gain_rate.png: scatter plot of month-over-month gains vs time

def plot_pre_post_inflection(
    benchmark_id: str,
    pre_gains: np.ndarray,
    post_gains: np.ndarray,
    out_dir: str,
) -> None: ...
# Saves pre_post_inflection.png: box plot pre-inflection vs post-inflection gain distributions

# --- Main ---
def main() -> None: ...
# Orchestrates: load → validate → analyze both benchmarks → print table → save JSON → 4 figures
# Exits with code 1 if H-E1 CSVs not found (prints actionable message to rerun H-E1)
```

---

## Configuration (inline constants in run.py)

```python
BENCHMARKS = {
    "glue":      "data/glue_timeseries_clean.csv",
    "superglue": "data/superglue_timeseries_clean.csv",
}
FIGURES_DIR  = "docs/youra_research/h-m1/figures"
RESULTS_JSON = "docs/youra_research/h-m1/results.json"
RHO_MONO_THRESHOLD  = 0.8
RHO_DECEL_THRESHOLD = -0.3
MIN_MONTHS_SPAN = 24
MIN_OBS         = 20
```

---

## Epic Tasks

| ID | Task | Description | Target File | Complexity | Breakdown | Depends On |
|----|------|-------------|-------------|------------|-----------|------------|
| E1 | Project setup | Create run.py skeleton, requirements.txt, figures dir, constants | code/run.py | 4 | 1+1+1+1 | — |
| E2 | Data loading & validation | load_timeseries(): read CSV, validate columns, assert time span/obs/variance | code/run.py | 7 | 2+1+2+2 | E1 |
| E3 | Gain rate computation | compute_gains(), split_inflection(): np.diff, pre/post split logic | code/run.py | 6 | 2+1+2+1 | E2 |
| E4 | Temporal analysis core | test_temporal_signal(): spearmanr(time,score), spearmanr(gain_time,gain), pre_post_ratio, pass flag | code/run.py | 10 | 2+2+4+2 | E3 |
| E5 | Results reporting | print_results_table(), save_results_json(): aligned stdout table + JSON output | code/run.py | 7 | 2+2+1+2 | E4 |
| E6 | Visualization | plot_gate_metrics(), plot_score_trajectory(), plot_gain_rate(), plot_pre_post_inflection() — 4 figures | code/run.py | 10 | 2+2+2+4 | E4 |
| E7 | Experiment runner | main(): orchestrate all steps for both benchmarks, handle missing H-E1 CSVs gracefully | code/run.py | 8 | 1+3+1+3 | E5, E6 |
| E8 | Test / sanity check | __main__ self-check: synthetic monotonic + decelerating series → assert rho values in expected range | code/run.py | 6 | 2+1+2+1 | E4 |

**Distribution**: High(9-13): [E4, E6], Medium(6-8): [E2, E3, E5, E7, E8], Low(4-5): [E1]

**Total**: 8 epic tasks, 58 complexity points.

---

## External Dependencies (Base Hypothesis)

| Artifact | Type | Path |
|----------|------|------|
| glue_timeseries_clean.csv | Data (read-only) | `data/glue_timeseries_clean.csv` |
| superglue_timeseries_clean.csv | Data (read-only) | `data/superglue_timeseries_clean.csv` |

**Expected CSV columns**: `months` (int, months-since-release), `monthly_max` (float, best score per month, normalized [0,1])

**Verified from**: H-E1 `03_architecture.md` preprocessing spec (preprocess() returns t_months, scores; monthly max aggregation). Actual H-E1 code not yet written — column names must be confirmed when H-E1 runs.
