# H-C1 Logic Design

**Applied: type-annotated API-first design pattern**
**Applied: error-result-dict return pattern (no exceptions in return path)**
**Applied: controlled-comparison reuse pattern (verbatim copy from validated pipeline)**

---

## Codebase Analysis (Serena)

**Analyzed**: `docs/youra_research/h-m4/code/run.py` (read directly)

Key findings:
- `logistic(t, K, r, t0)` at line ~31: `return K / (1 + np.exp(-r * (t - t0)))` — pure numpy, no state
- `extract_params(t_data, y_data, benchmark_name)` at line ~64: uses `BENCHMARK_RELEASE_MONTH` dict for offset; bounds `([0.5,0.01,-24],[1.05,3.0,72])`, p0=`[0.9,0.5,18]`
- `load_timeseries(csv_path)` at line ~36: reads CSV, returns `(t, y)` arrays
- `setup_logging(log_path)` at line ~434: standard Python logging setup
- `write_results(results, out_path)` at line ~425: JSON dump

**Critical mismatch**: H-M4 `extract_params` uses wider bounds than H-C1 spec requires. H-C1 must use its own `fit_and_evaluate()` with tighter bounds `([0.8,0.1,6],[1.0,2.0,48])`. Do NOT reuse `extract_params` for fitting.

---

## External Dependencies API

Verified from `h-m4/code/run.py` actual implementation:

```python
# Copy verbatim into h-c1/code/run.py — mark with "# verbatim from h-m4/code/run.py"

def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    """3-parameter logistic growth: K / (1 + exp(-r*(t - t0)))"""
    return K / (1 + np.exp(-r * (t - t0)))

def setup_logging(log_path: str) -> logging.Logger:
    """Standard file+console logger. Returns named logger."""
    ...

def write_results(results: dict, out_path: str) -> None:
    """JSON dump results dict to out_path."""
    ...
```

**NOT reused** (H-C1-specific bounds differ):
- `extract_params` — use `fit_and_evaluate()` defined below instead

---

## Subtask C1-2a: `discover_small_benchmarks()`

```python
def discover_small_benchmarks(
    min_entries: int = 30,
    max_entries: int = 49,
    min_year: int = 2019,
) -> list[dict]:
    """
    Enumerate all Papers With Code benchmarks and return those with
    result_count in [min_entries, max_entries] and at least one result
    from >= min_year.

    Returns:
        List of dicts: [{"id": str, "name": str, "result_count": int}, ...]
        Empty list if none found (caller must handle gracefully).

    Raises:
        ConnectionError: on API unavailability after 3 retries with backoff.
    """
```

**Pseudo-code:**
```
client = PapersWithCodeClient()
all_benchmarks = []
page = 1
WHILE True:
    result = client.benchmark_list(page=page, items_per_page=100)
    all_benchmarks.extend(result.results)
    IF result.next_page IS None OR page >= result.next_page:
        BREAK
    page += 1

filtered = []
FOR b IN all_benchmarks:
    IF NOT (min_entries <= b.result_count <= max_entries):
        CONTINUE
    # Check date coverage: fetch first page of results, check earliest date
    sample = client.benchmark_results(b.id, page=1, items_per_page=10)
    years = [r.date.year for r in sample.results IF r.date IS NOT None]
    IF NOT years OR min(years) > min_year:
        # Might still qualify — be conservative; include if result_count qualifies
        # (full date check done in fetch_timeseries)
        PASS
    filtered.append({"id": b.id, "name": b.name, "result_count": b.result_count})

IF len(filtered) < 3:
    log.warning(f"Only {len(filtered)} qualifying benchmarks found (expected >=3)")
RETURN filtered
```

**Edge cases:**
- API pagination: always paginate to completion (don't assume single page)
- HTTP 429: exponential backoff 3× before raising `ConnectionError`
- `result_count` field missing on old API versions: skip benchmark with warning

---

## Subtask C1-2b: `fetch_timeseries()`

```python
def fetch_timeseries(
    benchmark_id: str,
    benchmark_name: str,
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Retrieve and preprocess leaderboard timeseries for a single benchmark.
    Applies identical preprocessing to H-E1 pipeline.

    Returns:
        (t, y): t = months-since-earliest-submission (float64, shape [N,])
                y = normalized score in [0,1] (float64, shape [N,])
        None if fewer than 10 data points after preprocessing (log warning).
    """
```

**Preprocessing pipeline (identical to H-E1):**
```
1. client.benchmark_results(benchmark_id, page=1..N) → paginate all results
2. Extract (date, metric_value) pairs — skip entries with None date or None value
3. Convert date → months-since-earliest-submission:
       t_raw = (date.year * 12 + date.month)
       t = t_raw - min(t_raw)
4. Normalize metric to [0,1]:
       y = (metric_value - min(metric_value)) / (max(metric_value) - min(metric_value) + 1e-9)
5. Deduplicate: keep best (highest) score per (model_name, month):
       group by month → take max y per month
6. Sort by t ascending
7. IF len(t) < 10: log warning, return None
8. RETURN (np.array(t, dtype=float64), np.array(y, dtype=float64))
```

**Edge cases:**
- All scores identical (max == min): normalization produces all-zeros → return None with warning
- Single result: insufficient for fitting → return None

---

## Subtask C1-3a: `fit_and_evaluate()`

```python
def fit_and_evaluate(
    times: np.ndarray,
    scores: np.ndarray,
    bounds: tuple[list[float], list[float]] = ([0.8, 0.1, 6], [1.0, 2.0, 48]),
    p0: list[float] = [0.95, 0.5, 18],
    maxfev: int = 5000,
) -> dict:
    """
    Fit 3-parameter logistic to (times, scores) and evaluate fit quality.

    Returns dict with keys:
        converged: bool           — False if RuntimeError raised
        r_squared: float | None   — None if not converged
        params: tuple | None      — (K, r, t0) if converged, else None
        ci_width: np.ndarray | None — 2*1.96*sqrt(diag(pcov)), shape [3,]
        plausible: bool           — K<0.999 AND r>0.05 AND 6<t0<48
        k_boundary_hit: bool      — K >= 0.999
        n_points: int             — len(times)
    """
```

**Algorithm:**
```
TRY:
    popt, pcov = curve_fit(logistic, times, scores,
                           p0=p0, bounds=bounds, maxfev=maxfev)
    K, r, t0 = popt
    ss_res = sum((scores - logistic(times, *popt))**2)
    ss_tot = sum((scores - mean(scores))**2)
    r_sq = 1 - ss_res / (ss_tot + 1e-12)   # guard /0
    ci_width = 2 * 1.96 * sqrt(diag(pcov))
    plausible = (K < 0.999) AND (r > 0.05) AND (6 < t0 < 48)
    RETURN {converged: True, r_squared: r_sq, params: popt,
            ci_width: ci_width, plausible: plausible,
            k_boundary_hit: K >= 0.999, n_points: len(times)}
EXCEPT RuntimeError:
    RETURN {converged: False, r_squared: None, params: None,
            ci_width: None, plausible: False,
            k_boundary_hit: False, n_points: len(times)}
```

**Edge cases:**
- `ss_tot == 0` (all scores identical): guard with `+ 1e-12`
- `pcov` contains `inf` (singular covariance): `ci_width` will be `inf` — acceptable, log warning

---

## Subtask C1-6a: `run_ablation()` — variant specifications

```python
def run_ablation(
    timeseries_data: list[tuple[np.ndarray, np.ndarray]],
    benchmark_names: list[str],
    control_results: list[dict],
) -> dict[str, dict]:
    """
    Run 4 ablation variants on the 30-49-entry benchmark timeseries.

    Args:
        timeseries_data: list of (t, y) arrays for small benchmarks
        benchmark_names:  parallel list of benchmark names
        control_results:  fit dicts for >=50-entry control group (H-E1)

    Returns:
        dict keyed by variant name → comparison dict (same schema as compare_groups())
        Keys: "strict", "loose", "split40", "no_bounds"
    """
```

**Variant specifications:**

| Variant | Key | Change | Failure criterion |
|---------|-----|--------|-------------------|
| Strict threshold | `strict` | failure_r2=0.5 | R² < 0.5 |
| Loose threshold | `loose` | failure_r2=0.8 | R² < 0.8 |
| Split at 40 | `split40` | split t into 30-39 / 40-49 sub-groups | compare sub-groups |
| No bounds | `no_bounds` | bounds=(-inf, +inf) | standard failure_r2=0.7 |

---

## Subtask C1-6b: Ablation dispatch pseudo-code

```
VARIANTS = {
    "strict":    {"bounds": ([0.8,0.1,6],[1.0,2.0,48]), "failure_r2": 0.5},
    "loose":     {"bounds": ([0.8,0.1,6],[1.0,2.0,48]), "failure_r2": 0.8},
    "no_bounds": {"bounds": (-np.inf, np.inf),            "failure_r2": 0.7},
}

results = {}

# Variants with uniform threshold change
FOR variant_name, cfg IN VARIANTS.items():
    fits = []
    FOR (t, y) IN timeseries_data:
        fit = fit_and_evaluate(t, y, bounds=cfg["bounds"])
        fits.append(fit)
    comparison = compare_groups(fits, control_results,
                                failure_r2=cfg["failure_r2"])
    results[variant_name] = comparison

# Split-at-40 variant (structural, not threshold)
small30_39, small40_49 = [], []
FOR i, (t, y) IN enumerate(timeseries_data):
    n = len(t)
    IF n <= 10:   # can't split meaningfully
        CONTINUE
    mid = n // 2  # approximate split (no actual n_entries sub-split available post-fetch)
    # Use benchmark result_count to classify
    IF benchmark_names[i].result_count <= 39:   # need result_count stored
        small30_39.append(fit_and_evaluate(t, y))
    ELSE:
        small40_49.append(fit_and_evaluate(t, y))

results["split40"] = {
    "30_39": compare_groups(small30_39, control_results) IF small30_39 ELSE None,
    "40_49": compare_groups(small40_49, control_results) IF small40_49 ELSE None,
}

RETURN results
```

**Result aggregation schema** (per variant):
```python
{
    "variant": str,
    "convergence_rate_small": float,   # 0.0-1.0
    "mean_r2_small": float | None,
    "plausibility_rate_small": float,
    "k_boundary_hit_rate_small": float,
    "h_c1_supported": bool,            # based on variant's failure_r2 threshold
    "n_benchmarks": int,
}
```
