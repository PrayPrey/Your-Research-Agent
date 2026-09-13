---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
date: "2026-08-25"
---

# Logic: H-E1 — Logistic Growth Fit on Papers With Code

Applied: statistical-fitting-pipeline (scipy.optimize.curve_fit with AIC comparison)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze, Serena skipped
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E4: Model Fitting [Complexity: 12, Budget: 4 subtasks]

### API Signatures

```python
def fit_linear(t: np.ndarray, y: np.ndarray) -> dict:
    """Fit degree-1 polynomial; compute R² and AIC (k=2).
    t: [N,]  months_since_release (float)
    y: [N,]  normalized scores in [0, 1]
    Returns: {"coeffs": np.ndarray [2,], "r2": float, "aic": float}
    """
    ...

def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    """3-parameter logistic: K / (1 + exp(-r*(t-t0))).
    t: [N,] -> out: [N,]
    """
    ...

def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict:
    """Fit logistic via curve_fit; return params, CI, R², AIC, convergence flag.
    t: [N,], y: [N,]
    Returns: {
        "popt": np.ndarray [3,],   # [K, r, t0]
        "pcov": np.ndarray [3,3],  # covariance matrix
        "r2": float,
        "aic": float,
        "ci95": np.ndarray [3,],   # 1.96 * sqrt(diag(pcov))
        "converged": bool,
    }
    Raises: does NOT raise — catches RuntimeError/OptimizeWarning internally,
            sets converged=False and fills popt with last attempted values or NaN.
    """
    ...
```

### Key Algorithmic Steps

fit_linear:
```
1. coeffs = np.polyfit(t, y, deg=1)         # [2,]: [slope, intercept]
2. y_pred = np.polyval(coeffs, t)            # [N,]
3. ss_res = sum((y - y_pred)**2)
4. ss_tot = sum((y - y.mean())**2)
5. r2 = 1 - ss_res / ss_tot
6. n, k = len(t), 2
7. aic = n * np.log(ss_res / n) + 2 * k
8. return {"coeffs": coeffs, "r2": r2, "aic": aic}
```

fit_logistic:
```
1. p0 = [0.9, 0.5, np.median(t)]
2. bounds = ([0.8, 0.01, 0.0], [1.05, 5.0, 60.0])
3. try:
     with warnings.catch_warnings(record=True) as w:
         popt, pcov = curve_fit(logistic, t, y, p0=p0, bounds=bounds, maxfev=10000)
     converged = not any(issubclass(x.category, OptimizeWarning) for x in w)
   except RuntimeError:
     popt, pcov = np.full(3, np.nan), np.full((3,3), np.nan)
     converged = False
4. ci95 = 1.96 * np.sqrt(np.diag(pcov))     # [3,]
5. y_pred = logistic(t, *popt)               # [N,]
6. r2, aic = compute_r2_aic(y, y_pred, k=3)
7. return {"popt": popt, "pcov": pcov, "r2": r2, "aic": aic, "ci95": ci95, "converged": converged}
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| t | [N,] | months since release, float |
| y | [N,] | normalized score [0,1] |
| coeffs | [2,] | [slope, intercept] |
| popt | [3,] | [K, r, t0] |
| pcov | [3,3] | covariance from curve_fit |
| ci95 | [3,] | 95% CI per parameter |

### Subtasks [4/4 used]

| ID | Subtask | Parent Epic | Description | Est. Lines |
|----|---------|-------------|-------------|------------|
| L-E4-1 | logistic_function | E4 | Implement `logistic(t, K, r, t0)` with overflow guard via `np.clip` on exponent | 8 |
| L-E4-2 | fit_linear | E4 | `fit_linear()`: polyfit, R², AIC (k=2) | 15 |
| L-E4-3 | fit_logistic | E4 | `fit_logistic()`: curve_fit with warning capture, CI from pcov diagonal | 35 |
| L-E4-4 | r2_aic_helper | E4 | Internal `_r2_aic(y, y_pred, k)` reused by both fit functions | 10 |

---

## E5: Visualization [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
def plot_all(
    benchmark_id: str,
    t: np.ndarray,           # [N,] months
    y: np.ndarray,           # [N,] scores
    linear: dict,            # from fit_linear()
    logistic_result: dict,   # from fit_logistic()
    out_dir: str,
) -> None:
    """Save scatter+fit plot and residuals panel for one benchmark.
    Writes: {out_dir}/logistic_fit_{benchmark_id}.png
            {out_dir}/residuals_{benchmark_id}.png
    """
    ...

def plot_gate_metrics(results: dict[str, dict], out_dir: str) -> None:
    """Bar chart of R² per benchmark with 0.9 threshold line.
    results keys: benchmark_id strings; values contain "logistic_result" dict.
    Writes: {out_dir}/gate_metrics.png
    """
    ...

def plot_parameter_summary(results: dict[str, dict], out_dir: str) -> None:
    """Table figure of K, r, t0 with 95% CI for all benchmarks.
    Writes: {out_dir}/parameter_summary.png
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Parent Epic | Description | Est. Lines |
|----|---------|-------------|-------------|------------|
| L-E5-1 | plot_all | E5 | Scatter + logistic curve overlay + residuals subplot; uses `np.linspace` for smooth curve | 45 |
| L-E5-2 | plot_gate_and_params | E5 | `plot_gate_metrics()` bar chart + `plot_parameter_summary()` matplotlib table | 40 |

---

## E3: Preprocessing [Complexity: 7, Budget: 1 subtask]

### API Signatures

```python
def preprocess(
    raw: list[dict],          # [{"date": str|None, "score": float}, ...]
    release_date: str,        # "YYYY-MM-DD"
    min_date: str = "2019-01-01",
    min_entries: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """Filter, convert, normalize, dedup raw API entries.
    Returns: (t_months [M,], scores [M,]) sorted by t ascending.
    Raises: ValueError if entries after dedup < min_entries.
    """
    ...
```

### Key Algorithmic Steps

```
1. Drop entries where date is None
2. Parse dates; drop entries where date < min_date
3. t_raw = (date - release_date).days / 30.44          # float months
4. y_raw = score / 100.0                               # normalize to [0,1]
5. month_bin = np.floor(t_raw).astype(int)             # integer month bins
6. Dedup: for each unique bin, keep row with max y
7. Sort by t ascending
8. if len(t) < min_entries: raise ValueError(f"Only {len(t)} entries after dedup, need {min_entries}")
9. return t.astype(np.float64), y.astype(np.float64)   # [M,], [M,]
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| t_months | [M,] | M = unique month bins after dedup |
| scores | [M,] | normalized [0,1] |

### Subtasks [1/1 used]

| ID | Subtask | Parent Epic | Description | Est. Lines |
|----|---------|-------------|-------------|------------|
| L-E3-1 | preprocess | E3 | All 6 pipeline steps: null filter, date filter, month convert, normalize, dedup, eligibility check | 35 |

---

## Supporting Functions (E2 / E6 — reference only, no subtask budget allocated here)

```python
def fetch_benchmark(benchmark_id: str, max_retries: int = 3) -> list[dict]:
    """Paginate PWC API; retry with exponential backoff on failure.
    Returns: list of {"date": str|None, "score": float} dicts.
    Raises: RuntimeError after max_retries exhausted.
    """
    ...

def evaluate(linear: dict, logistic_result: dict) -> dict:
    """Summarize comparison between linear and logistic fit.
    Returns: {
        "converged": bool,
        "r2": float,           # logistic R²
        "delta_aic": float,    # AIC(logistic) - AIC(linear)
        "params": {
            "K": float, "K_ci95": float,
            "r": float, "r_ci95": float,
            "t0": float, "t0_ci95": float,
        }
    }
    """
    ...

def main() -> None:
    """Orchestrate: fetch → preprocess → fit → evaluate → plot → print → save JSON.
    Exit code 0 on PASS, 1 on FAIL (any benchmark fails gate).
    """
    ...
```
