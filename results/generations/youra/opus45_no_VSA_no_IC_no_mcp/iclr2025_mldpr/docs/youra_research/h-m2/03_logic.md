# Logic: h-m2 (MECHANISM — Temporal Prediction)

**Applied**: Statistical-regression-with-resampling pattern (OLS + bootstrap CI + LOO-CV for small-N).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (`metrics.py`, `data.py`, `config.py`), not from 03_architecture.md spec.
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**: `DNSIComputer.compute_dnsi`, `DNSIComputer._compute_windowed_improvements`, `load_data`, `match_target_benchmarks`, `extract_sota_history`, `CONFIG`, `TARGET_BENCHMARKS`

**Critical divergences from PRD/brief pseudo-code** (brief re-implements DNSI logic from scratch, diverging from actual h-e1 algorithm):
- Actual `_compute_windowed_improvements` computes **running-max deltas** per window (`window_max - prev_max`, only if improved), NOT `entropy(improvements + 1e-10)` — it uses `probs = deltas / deltas.sum()` then `entropy(probs)`. h-m2 MUST delegate to h-e1's `DNSIComputer.compute_dnsi` rather than reimplementing.
- `sota_history` param is `list[tuple[datetime, float]]`, already parsed — NOT raw JSON dicts with `"date"`/`"accuracy"` keys as brief's loader implies.
- `ObjectNet` is absent from `TARGET_BENCHMARKS`/`load_data()` output — must reuse matched `"ImageNet"` entry's `history`/`difficulty_proxy` for ObjectNet's DNSI (per PRD note: "ObjectNet uses ImageNet SOTA history").
- `DNSIComputer.__init__` takes only `window_months`; no `cutoff_date` — h-m2's `TemporalDNSIComputer` wraps it, does NOT subclass with overridden `compute_dnsi`.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
CONFIG: dict  # {"data_dir": "data/pwc", "min_sota_entries": 15, "min_history_years": 3, ...}
TARGET_BENCHMARKS: dict[str, int | None]  # {"ImageNet": 1000, "CIFAR-10": 10, "CIFAR-100": 100, ...}

# From: h-e1/code/data.py (ACTUAL CODE)
def load_data() -> dict:
    """Returns {name: {history: list[tuple[datetime,float]], difficulty_proxy: int|None,
    original_name: str, entry_count: int}} or {} on failure."""
    ...

def extract_sota_history(benchmark_data: dict) -> list[tuple]:
    """Extract (date, accuracy) pairs from raw table dict. Not needed if using load_data()."""
    ...

# From: h-e1/code/metrics.py (ACTUAL CODE)
class DNSIComputer:
    def __init__(self, window_months: int = 6): ...
    def compute_dnsi(
        self, sota_history: list[tuple[datetime, float]], difficulty_proxy: int | None
    ) -> float | None:
        """Windowed running-max improvements -> Shannon entropy / log(difficulty_proxy),
        clipped to CONFIG['dnsi_valid_range']. Returns None if <2 entries, no proxy, or no improvement."""
        ...

def validate_dnsi(dnsi_value: float | None) -> bool: ...
```

**Verified from**: `h-e1/code/metrics.py`, `h-e1/code/data.py`, `h-e1/code/config.py` (actual implementation).

**Import mechanism**: `sys.path.insert(0, H_E1_CODE_DIR)` in `train.py` before `from config import CONFIG as E1_CONFIG, TARGET_BENCHMARKS`, `from data import load_data`, `from metrics import DNSIComputer`. h-m2's own `config.py` is imported normally (no path conflict — different module name space avoided by aliasing `E1_CONFIG`).

---

## A-1: config.py [Complexity: 4, Budget: 4]

**Applied**: Standard config dict pattern (matches h-e1 style).

```python
CUTOFF_DATE: str = "2019-01-01"
MIN_HISTORY_YEARS_PRE_CUTOFF: int = 5
MIN_PRE_CUTOFF_ENTRIES: int = 10
N_BOOTSTRAP: int = 10000
SEED: int = 1
R2_PASS_THRESHOLD: float = 0.3
R2_FAIL_THRESHOLD: float = 0.1
LOO_R2_THRESHOLD: float = 0.1
CI_LOWER_THRESHOLD: float = 0.1
FIGURES_DIR: str = "figures"
H_E1_CODE_DIR: str = "../../h-e1/code"

GAP_GROUND_TRUTH: dict[str, dict] = {
    "ImageNet":   {"gap": 0.125, "source": "Recht2019"},
    "CIFAR-10":   {"gap": 0.04,  "source": "Recht2019"},
    "CIFAR-100":  {"gap": 0.05,  "source": "Recht2019-scaled"},
    "ObjectNet":  {"gap": 0.425, "source": "Barbu2019", "uses_history_of": "ImageNet"},
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Cutoff/threshold constants | CUTOFF_DATE, MIN_* , R2_* thresholds |
| L-1-2 | GAP_GROUND_TRUTH dict | 4 benchmarks incl. ObjectNet `uses_history_of` link |
| L-1-3 | Path constants | FIGURES_DIR, H_E1_CODE_DIR |
| L-1-4 | Bootstrap/seed constants | N_BOOTSTRAP, SEED |

---

## A-2: h-e1 data reuse bridge [Complexity: 6, Budget: 6]

**Applied**: sys.path injection pattern for cross-hypothesis code reuse.

```python
# in train.py, top of file
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), H_E1_CODE_DIR))
from config import CONFIG as E1_CONFIG, TARGET_BENCHMARKS  # noqa: E402
from data import load_data  # noqa: E402
from metrics import DNSIComputer  # noqa: E402

def load_matched_benchmarks() -> dict:
    """Calls h-e1 load_data(). Returns {} and prints error if empty."""
    matched = load_data()  # {name: {history, difficulty_proxy, original_name, entry_count}}
    if not matched:
        print("[BRIDGE] FAILED: h-e1 load_data() returned no benchmarks")
    return matched
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | sys.path injection | Insert H_E1_CODE_DIR before h-e1 imports |
| L-2-2 | load_data() call + validation | Wrap call, verify non-empty, log |
| L-2-3 | Format verification | Assert `history` is `list[tuple[datetime,float]]` per entry |
| L-2-4 | (0 budget — no additional subtask; folded into L-2-2) | |

---

## A-3: TemporalDNSIComputer [Complexity: 8, Budget: 8]

**Applied**: Wrapper/delegation pattern (compose, don't subclass, since h-e1 `compute_dnsi` has no cutoff param).

### API Signatures

```python
from datetime import datetime
from metrics import DNSIComputer  # h-e1, injected via sys.path

class TemporalDNSIComputer:
    def __init__(self, window_months: int = 6, cutoff_date: str = CUTOFF_DATE):
        self.cutoff = datetime.fromisoformat(cutoff_date)
        self._dnsi = DNSIComputer(window_months=window_months)  # delegate

    def compute_dnsi_pre_cutoff(
        self,
        sota_history: list[tuple[datetime, float]],  # full history from load_data()
        difficulty_proxy: int | None,
    ) -> float | None:
        """Filter history < cutoff, enforce min entries/years, delegate to h-e1 DNSIComputer."""
        ...
```

### Pseudo-code: `compute_dnsi_pre_cutoff`

```
1. pre = [(dt, acc) for dt, acc in sota_history if dt < self.cutoff]
2. if len(pre) < MIN_PRE_CUTOFF_ENTRIES: return None
3. span_years = (pre[-1][0] - pre[0][0]).days / 365   # pre already sorted (from load_data)
4. if span_years < MIN_HISTORY_YEARS_PRE_CUTOFF: return None
5. return self._dnsi.compute_dnsi(pre, difficulty_proxy)   # delegate windowing+entropy to h-e1
```

### Error Handling

- Empty/None `sota_history` -> `pre = []` -> step 2 returns `None` (no exception).
- `difficulty_proxy is None` -> delegated `compute_dnsi` returns `None` (h-e1 handles it).
- Unsorted input: `load_data()` guarantees sorted history (h-e1 `extract_sota_history` sorts); no re-sort needed, but defensively `sorted(pre, key=lambda t: t[0])` before span/window calc costs nothing — include it.

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `__init__` w/ cutoff parse + h-e1 DNSIComputer instantiation | 2 |
| L-3-2 | Cutoff filtering + sort defensiveness | 2 |
| L-3-3 | Min-entries + min-years checks, delegate call | 3 |
| L-3-4 | Error handling (None/empty guards) | 1 |

---

## A-4: Benchmark-gap alignment [Complexity: 7, Budget: 7]

**Applied**: Dict-join pattern, ObjectNet special-cased via `uses_history_of`.

```python
def align_dnsi_gap(
    matched: dict,                # from load_data()
    dnsi_computer: "TemporalDNSIComputer",
) -> tuple[list[str], list[float], list[float]]:
    """Returns (benchmark_names, dnsi_pre[], gap_post[]) aligned arrays, skipping
    benchmarks with None DNSI or missing GAP_GROUND_TRUTH entry."""
    ...
```

### Pseudo-code

```
names, dnsi_vals, gap_vals = [], [], []
for bench, meta in GAP_GROUND_TRUTH.items():
    source_bench = meta.get("uses_history_of", bench)   # ObjectNet -> ImageNet
    if source_bench not in matched:
        print(f"[ALIGN] SKIP {bench}: source '{source_bench}' not matched")
        continue
    entry = matched[source_bench]
    dnsi = dnsi_computer.compute_dnsi_pre_cutoff(entry["history"], entry["difficulty_proxy"])
    if dnsi is None:
        print(f"[ALIGN] SKIP {bench}: insufficient pre-cutoff DNSI data")
        continue
    names.append(bench); dnsi_vals.append(dnsi); gap_vals.append(meta["gap"])
return names, dnsi_vals, gap_vals
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dnsi_vals (as np.ndarray) | [n] | n <= 4 |
| gap_vals (as np.ndarray) | [n] | aligned by index to dnsi_vals |

### Error Handling

- If `len(names) < 2` after loop -> `train.py` aborts pipeline before regression (can't fit OLS on <2 points), prints `"[ALIGN] FAILED: <2 aligned benchmarks, cannot regress"`, returns gate `"FAIL"`.

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Iterate GAP_GROUND_TRUTH, resolve `uses_history_of` | 2 |
| L-4-2 | Call `compute_dnsi_pre_cutoff`, skip-on-None w/ logging | 2 |
| L-4-3 | Build aligned (names, dnsi, gap) lists | 2 |
| L-4-4 | Guard for `n < 2` before returning | 1 |

---

## A-5: TemporalPredictionAnalyzer [Complexity: 12, Budget: 12]

**Applied**: OLS + bootstrap resampling + LOO-CV for small-N regression (standard scipy/sklearn).

### API Signatures

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class TemporalPredictionAnalyzer:
    def __init__(self, n_bootstrap: int = N_BOOTSTRAP, seed: int = SEED):
        self.n_bootstrap = n_bootstrap
        self.rng = np.random.default_rng(seed)

    def analyze(self, dnsi_pre: np.ndarray, gap_post: np.ndarray) -> dict:
        """dnsi_pre, gap_post: [n]. Returns dict with n, r2, adj_r2, loo_r2,
        ci_95_lower, ci_95_upper, slope, intercept, hypothesis_supported."""
        ...

    def _bootstrap_r2(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Returns [k] array, k <= n_bootstrap (degenerate resamples dropped)."""
        ...

    def _loo_cv(self, x: np.ndarray, y: np.ndarray) -> float:
        """Returns scalar LOO-CV R²."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dnsi_pre, gap_post | [n] | n = 3 or 4 (small-N) |
| X (reshaped) | [n, 1] | sklearn requires 2D input |
| bootstrap_r2 | [k] | k <= n_bootstrap, filtered for finite/valid |

### Pseudo-code: `analyze`

```
1. n = len(dnsi_pre)
2. if n < 2: return {"n": n, "error": "insufficient_data", "hypothesis_supported": False}
3. X = dnsi_pre.reshape(-1, 1); y = gap_post
4. model = LinearRegression().fit(X, y)
5. y_pred = model.predict(X)
6. r2 = r2_score(y, y_pred)
7. adj_r2 = 1 - (1-r2)*(n-1)/(n-2) if n > 2 else float('nan')   # guard n=2 div-by-zero
8. bootstrap_r2 = self._bootstrap_r2(dnsi_pre, gap_post)
9. ci_lower, ci_upper = np.percentile(bootstrap_r2, [2.5, 97.5]) if bootstrap_r2.size else (nan, nan)
10. loo_r2 = self._loo_cv(dnsi_pre, gap_post)
11. return {n, r2, adj_r2, loo_r2, ci_95_lower, ci_95_upper,
            slope: model.coef_[0], intercept: model.intercept_,
            hypothesis_supported: r2 > R2_PASS_THRESHOLD}
```

### Pseudo-code: `_bootstrap_r2`

```
n = len(x); r2_values = []
for _ in range(self.n_bootstrap):
    idx = self.rng.integers(0, n, size=n)          # seeded RNG, not global np.random
    if len(np.unique(idx)) <= 1: continue           # need variance to fit
    X_boot = x[idx].reshape(-1, 1); y_boot = y[idx]
    model = LinearRegression().fit(X_boot, y_boot)
    r2 = r2_score(y_boot, model.predict(X_boot))
    if np.isfinite(r2): r2_values.append(r2)
return np.array(r2_values)
```

### Pseudo-code: `_loo_cv`

```
n = len(x); preds, actuals = [], []
for i in range(n):
    X_train = np.delete(x, i).reshape(-1, 1); y_train = np.delete(y, i)
    model = LinearRegression().fit(X_train, y_train)
    preds.append(model.predict(x[i].reshape(1, -1))[0])
    actuals.append(y[i])
ss_res = sum((actuals - preds)**2); ss_tot = sum((actuals - mean(actuals))**2)
return 1 - ss_res/ss_tot if ss_tot > 0 else 0.0
```

### Error Handling

- `n < 2`: `analyze` short-circuits, returns error dict; caller (`train.py`) must check `"error"` key before proceeding to gate/figures.
- `n == 2`: `adj_r2 = nan` (formula divides by `n-2`); reported as-is, not treated as failure.
- Bootstrap: seeded via `np.random.default_rng(SEED)` instance (NFR-1 reproducibility) — **not** global `np.random.seed`, since brief's pseudo-code uses global state (avoid; use instance RNG for isolation).
- All-degenerate bootstrap (`bootstrap_r2.size == 0`, only possible if n=1, already blocked by step 2 guard) — defensive `if bootstrap_r2.size` check before percentile.

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `__init__` + seeded RNG | 3 |
| L-5-2 | `analyze`: OLS fit, r2, adj_r2 w/ n=2 guard | 2 |
| L-5-3 | `_bootstrap_r2` w/ seeded resampling, degenerate-skip | 4 |
| L-5-4 | `_loo_cv` + CI percentile assembly in `analyze` | 3 |

---

## A-6: Gate evaluation [Complexity: 5, Budget: 5]

**Applied**: Threshold-gate pattern.

```python
def check_gate(results: dict) -> str:
    """'PASS' if r2 > R2_PASS_THRESHOLD, 'FAIL' if r2 < R2_FAIL_THRESHOLD, else 'MARGINAL'.
    Returns 'FAIL' immediately if results contains 'error' key."""
    if "error" in results:
        return "FAIL"
    r2 = results["r2"]
    if r2 > R2_PASS_THRESHOLD:
        return "PASS"
    if r2 < R2_FAIL_THRESHOLD:
        return "FAIL"
    return "MARGINAL"

def summarize(results: dict) -> dict:
    """Adds: slope_negative (bool), loo_pass (bool: loo_r2 > LOO_R2_THRESHOLD),
    ci_lower_pass (bool: ci_95_lower > CI_LOWER_THRESHOLD)."""
    ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | `check_gate` PASS/FAIL/MARGINAL logic + error short-circuit | 1 |
| L-6-2 | `summarize`: slope_negative, loo_pass flags | 2 |
| L-6-3 | `summarize`: ci_lower_pass flag | 1 |
| L-6-4 | Merge summary into results dict for JSON export | 1 |

---

## A-7: Visualization [Complexity: 6, Budget: 6]

**Applied**: matplotlib scatter/hist standard patterns.

```python
import matplotlib.pyplot as plt

def generate_figures(
    dnsi: np.ndarray,      # [n]
    gap: np.ndarray,       # [n]
    results: dict,
    bootstrap_r2: np.ndarray,  # [k]
    out_dir: str = FIGURES_DIR,
) -> None:
    """Writes: scatter_regression.png (required), bootstrap_hist.png, loo_pred_vs_actual.png."""
    ...
```

### Pseudo-code

```
1. scatter_regression.png:
   scatter(dnsi, gap); plot regression line using results["slope"], results["intercept"]
   over x-range [min(dnsi), max(dnsi)]; annotate f"R2={results['r2']:.3f}"
2. bootstrap_hist.png (if bootstrap_r2.size > 0):
   hist(bootstrap_r2, bins=50); axvline at ci_95_lower, ci_95_upper
3. loo_pred_vs_actual.png:
   recompute LOO predictions (or pass through from analyzer); scatter(actual, predicted);
   plot y=x reference line
```

### Error Handling

- `os.makedirs(out_dir, exist_ok=True)` before saving.
- `n < 2`: skip figure generation entirely, log `"[FIGURES] SKIP: insufficient data"`.

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Scatter + regression line + R² annotation (required) | 2 |
| L-7-2 | Bootstrap histogram w/ CI bands | 1 |
| L-7-3 | LOO pred-vs-actual scatter w/ y=x line | 1 |
| L-7-4 | out_dir creation + n<2 skip guard | 2 |

---

## A-8: Pipeline integration (train.py) [Complexity: 7, Budget: 7]

**Applied**: Orchestrator entrypoint pattern (mirrors h-e1 train.py structure).

```python
def run_pipeline() -> dict:
    """Full pipeline: bridge -> DNSI -> alignment -> analysis -> gate -> figures -> JSON export."""
    ...

if __name__ == "__main__":
    run_pipeline()
```

### Pseudo-code

```
1. matched = load_matched_benchmarks()                      # A-2
   if not matched: print FAILED, return {"gate_result": "FAIL"}
2. dnsi_computer = TemporalDNSIComputer(cutoff_date=CUTOFF_DATE)  # A-3
3. names, dnsi_vals, gap_vals = align_dnsi_gap(matched, dnsi_computer)  # A-4
   if len(names) < 2: print FAILED, return {"gate_result": "FAIL"}
4. print(f"[TEMPORAL] Analyzing {len(names)} benchmark predictions...")   # activation
5. analyzer = TemporalPredictionAnalyzer(n_bootstrap=N_BOOTSTRAP, seed=SEED)  # A-5
   results = analyzer.analyze(np.array(dnsi_vals), np.array(gap_vals))
   if "error" in results: print FAILED, return {"gate_result": "FAIL", **results}
6. gate = check_gate(results); results = {**results, **summarize(results), "gate_result": gate, "benchmarks": names}
7. if gate == "PASS": print(f"[TEMPORAL] SUCCESS: R2 = {results['r2']:.3f} > 0.3")
   elif gate == "FAIL": print(f"[TEMPORAL] FAILED: R2 = {results['r2']:.3f} < 0.1")
   else: print(f"[TEMPORAL] MARGINAL: R2 = {results['r2']:.3f}")
8. bootstrap_r2 = analyzer._bootstrap_r2(np.array(dnsi_vals), np.array(gap_vals))
   generate_figures(np.array(dnsi_vals), np.array(gap_vals), results, bootstrap_r2, FIGURES_DIR)  # A-7
9. write results dict to results.json
10. return results
```

### Error Handling

- Any stage failure (empty `matched`, `<2` aligned points, `analyze` error) short-circuits with `gate_result: "FAIL"` and skips downstream figure/JSON steps that depend on missing data (JSON of partial results still written).
- `NFR-2` (<60s): no explicit timeout enforced in code — n<=4 bootstrap of 10k iterations is O(10k) trivial; no action needed.

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Bridge call + failure short-circuit | 1 |
| L-8-2 | DNSI computer + alignment wiring + activation log | 3 |
| L-8-3 | Analyzer call + error short-circuit | 1 |
| L-8-4 | Gate/summarize + success/fail/marginal logging + figures + JSON export | 2 |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" lines)
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments / tables
- [x] Subtask counts match budgets (4+6+8+7+12+5+6+7 = 55, matches architecture total)
- [x] "Codebase Analysis (Serena)" section included
- [x] External Dependencies API section included (base_hypothesis scenario)
