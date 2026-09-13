---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
date: "2026-08-25"
---

# Architecture: H-E1 — Logistic Growth Fit on Papers With Code

Applied: statistical-fitting-pipeline (fetch → preprocess → fit → evaluate → plot)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Serena skipped.

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── run.py          # single entry point: fetch + preprocess + fit + eval + plot
│   └── requirements.txt
└── figures/            # output directory (created at runtime)
    ├── gate_metrics.png
    ├── logistic_fit_glue.png
    ├── logistic_fit_superglue.png
    ├── residuals.png
    └── parameter_summary.png
```

Single-file approach: all logic in `run.py`. No modules, no packages. This is a PoC script.

---

## Module Structure

### run.py — top-level functions (no classes needed)

**Dependencies**: paperswithcode-client, scipy, numpy, matplotlib

```python
# --- Data retrieval ---
def fetch_benchmark(benchmark_id: str, max_retries: int = 3) -> list[dict]: ...
# Returns list of {"date": str | None, "score": float} dicts. Retries with backoff.

# --- Preprocessing ---
def preprocess(
    raw: list[dict],
    release_date: str,  # "YYYY-MM-DD"
    min_date: str = "2019-01-01",
    min_entries: int = 50,
) -> tuple[np.ndarray, np.ndarray]: ...
# Returns (t_months, scores) after filter, normalize, dedup. Raises ValueError if < min_entries.

# --- Baseline model ---
def fit_linear(t: np.ndarray, y: np.ndarray) -> dict: ...
# Returns {"coeffs": np.ndarray, "r2": float, "aic": float}

# --- Logistic model ---
def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray: ...

def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict: ...
# Returns {"popt": np.ndarray, "pcov": np.ndarray, "r2": float,
#          "aic": float, "ci95": np.ndarray, "converged": bool}

# --- Evaluation ---
def evaluate(linear: dict, logistic: dict) -> dict: ...
# Returns {"converged": bool, "r2": float, "delta_aic": float, "params": dict}

# --- Visualization ---
def plot_all(
    benchmark_id: str,
    t: np.ndarray,
    y: np.ndarray,
    linear: dict,
    logistic: dict,
    out_dir: str,
) -> None: ...
# Saves: logistic_fit_{benchmark_id}.png, residuals patch contribution

def plot_gate_metrics(results: dict[str, dict], out_dir: str) -> None: ...
# Saves: gate_metrics.png (R² bar chart with 0.9 threshold line)

def plot_parameter_summary(results: dict[str, dict], out_dir: str) -> None: ...
# Saves: parameter_summary.png (K, r, t0 table with 95% CI)

# --- Main ---
def main() -> None: ...
# Orchestrates all steps, prints structured summary to stdout, writes results.json
```

---

## Configuration (inline constants in run.py)

```python
BENCHMARKS = {
    "glue":      {"release_date": "2019-02-01"},
    "super-glue": {"release_date": "2019-05-01"},
}
FIGURES_DIR = "docs/youra_research/h-e1/figures"
RESULTS_JSON = "docs/youra_research/h-e1/results.json"
CURVE_FIT_BOUNDS = ([0.8, 0.01, 0.0], [1.05, 5.0, 60.0])
CURVE_FIT_P0_TEMPLATE = [0.9, 0.5, None]  # t0 = median(t) at runtime
CURVE_FIT_MAXFEV = 10000
MIN_ENTRIES = 50
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Project setup | Create run.py skeleton, requirements.txt, figures dir | 4 | 1+1+1+1 |
| E2 | Data retrieval | fetch_benchmark() with pagination + retry/backoff | 8 | 2+2+2+2 |
| E3 | Preprocessing | preprocess(): filter, convert, normalize, dedup, eligibility check | 7 | 2+1+2+2 |
| E4 | Model fitting | fit_linear() + fit_logistic() with convergence detection, R², AIC, CI | 12 | 3+2+4+3 |
| E5 | Visualization | plot_all(), plot_gate_metrics(), plot_parameter_summary() — 5 figures | 9 | 2+2+2+3 |
| E6 | Evaluation & output | evaluate(), main() orchestration, JSON + stdout results | 7 | 2+2+1+2 |

**Distribution**: High(10-13): [E4], Medium(7-9): [E3, E5, E6], Low(4-6): [E1, E2]

**Total**: 6 epic tasks, estimated 47 complexity points.
