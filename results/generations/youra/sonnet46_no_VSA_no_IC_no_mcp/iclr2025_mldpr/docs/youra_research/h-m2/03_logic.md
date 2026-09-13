# Logic Design: H-M2 — AIC-Based Model Comparison

**Applied:** reuse-prior-experiment-api pattern (H-E1 fitting.py verified)
**Applied:** aic-model-selection pattern (Burnham & Anderson 2002; n*log(RSS/n)+2k formula)

---

## Codebase Analysis (Serena)

**Analyzed:** `docs/youra_research/h-e1/code/fitting.py`, `docs/youra_research/h-m1/code/run.py`

**Verified signatures from actual H-E1 code:**

| Function | Actual Signature | Notes |
|----------|-----------------|-------|
| `_r2_aic` | `(y: ndarray, y_pred: ndarray, k: int) -> tuple[float, float]` | Returns (r2, aic); AIC = n*log(ss_res/n)+2k |
| `logistic` | `(t: ndarray, K: float, r: float, t0: float) -> ndarray` | Overflow guard via np.clip |
| `fit_logistic` | `(t: ndarray, y: ndarray) -> dict` | Keys: popt, pcov, r2, aic, ci95, converged |
| `fit_linear` | `(t: ndarray, y: ndarray) -> dict` | Keys: coeffs, r2, aic; uses np.polyfit deg=1 |

**Critical finding:** Actual H-E1 bounds differ from PRD:
- Actual: p0=[0.9, 0.5, median(t)*0.3], bounds=([0.8,0.01,-20], [1.05,5.0,60]), maxfev=10000
- PRD stated: p0=[0.95,0.5,18], bounds K∈[0.8,1.0] etc. — **trust the code, not the PRD**

**Column names:** H-M1 run.py uses `months` (int) and `monthly_max` (float) — confirmed.

---

## External Dependencies API

Verified from `docs/youra_research/h-e1/code/fitting.py`:

```python
# Copy these inline into h-m2/code/run.py

def _r2_aic(y: np.ndarray, y_pred: np.ndarray, k: int) -> tuple[float, float]:
    """Returns (r2: float, aic: float). AIC = n*log(RSS/n) + 2k."""
    # ss_res = sum((y - y_pred)^2); aic = inf if ss_res <= 0

def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    """3-param logistic with clip guard. Returns predicted y."""

def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict:
    """Returns: {popt: ndarray[3], pcov: ndarray[3,3], r2: float,
                 aic: float, ci95: ndarray[3], converged: bool}"""
    # Uses: p0=[0.9,0.5,median(t)*0.3], bounds=([0.8,0.01,-20],[1.05,5.0,60]), maxfev=10000

def fit_linear(t: np.ndarray, y: np.ndarray) -> dict:
    """Returns: {coeffs: ndarray[2], r2: float, aic: float}. k=2."""
```

---

## Full API Signatures: h-m2/code/run.py

### Data Loading

```python
def load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load timeseries CSV. Columns: 'months' (int), 'monthly_max' (float).
    Returns: (t: ndarray, y: ndarray) sorted by t ascending.
    Raises: FileNotFoundError with clear message if csv_path missing.
    """
```

### New Models (H-M2 contribution)

```python
def fit_power_law(t: np.ndarray, y: np.ndarray) -> dict:
    """
    Fit a*(t+1)^b via curve_fit. +1 avoids t=0 singularity.
    p0=[0.5, 0.3], bounds=([0.0, 0.0], [2.0, 1.0]), maxfev=5000
    k=2 parameters.
    Returns: {popt: ndarray[2], r2: float, aic: float, converged: bool}
    """

def compute_delta_aic(fit_a: dict, fit_b: dict) -> float:
    """
    Returns fit_a['aic'] - fit_b['aic'].
    Negative = fit_a preferred. Used as: delta_log_vs_lin = logistic_aic - linear_aic.
    """
```

### Gate Logic

```python
def verify_gate(results: dict) -> tuple[bool, dict]:
    """
    results keys: 'glue', 'superglue'; each has:
      delta_log_vs_lin: float  (negative = logistic preferred)
      delta_log_vs_pl: float

    Primary gate:   delta_log_vs_lin < -4 for BOTH benchmarks
    Secondary gate: delta_log_vs_pl  < -2 for BOTH benchmarks

    Returns: (gate_pass: bool, indicators: dict)
    indicators keys:
      logistic_converged_glue, logistic_converged_sg: bool
      delta_aic_passes_glue, delta_aic_passes_sg: bool (primary)
      power_passes_glue, power_passes_sg: bool (secondary)
      gate_pass: bool
    """
```

### Figures API (4 required — subtask L-5-1, L-5-2)

```python
def plot_gate_metrics(results: dict, out_dir: Path) -> None:
    """
    Subtask L-5-1: Gate metrics bar chart.
    Grouped bars: [GLUE, SuperGLUE] x [delta_log_vs_lin, delta_log_vs_pl]
    Horizontal threshold lines at -4 (primary) and -2 (secondary).
    Saves: out_dir / 'gate_metrics.png'
    """

def plot_model_fits(
    data: dict,   # {'glue': (t, y), 'superglue': (t, y)}
    fits: dict,   # {'glue': {logistic, linear, power}, 'superglue': {...}}
    out_dir: Path
) -> None:
    """
    Subtask L-5-2: Model fit overlay.
    2 subplots (GLUE, SuperGLUE): scatter + logistic + linear + power-law curves.
    Legend with R² values. Saves: out_dir / 'model_fits.png'
    """

def plot_residuals(data: dict, fits: dict, out_dir: Path) -> None:
    """
    Residuals vs time for all 3 models x 2 benchmarks (2x3 subplots or 2 subplots each).
    Shows systematic underfitting of linear/power-law in plateau region.
    Saves: out_dir / 'residuals.png'
    """

def plot_aic_comparison(results: dict, out_dir: Path) -> None:
    """
    Grouped bar chart: raw AIC values (logistic, linear, power_law) per benchmark.
    Saves: out_dir / 'aic_comparison.png'
    """
```

### Output

```python
def write_results(results: dict, gate: tuple[bool, dict], out_path: Path) -> None:
    """
    Writes results.json with:
      gate_pass: bool
      indicators: dict
      glue: {aic_logistic, aic_linear, aic_power, delta_log_vs_lin, delta_log_vs_pl,
             logistic_params: {K, r, t0}}
      superglue: {same structure}
    """

def setup_logging(log_path: Path) -> logging.Logger:
    """FileHandler → experiment.log, StreamHandler → stdout. Level INFO."""
```

### Entry Point

```python
def main() -> None:
    """
    Flow:
    1. setup_logging(h-m2/experiment.log)
    2. load_timeseries for GLUE and SuperGLUE (from ../h-e1/code/data/)
    3. For each benchmark: fit_logistic, fit_linear, fit_power_law
    4. compute_delta_aic for each pair
    5. verify_gate(results)
    6. plot_gate_metrics, plot_model_fits, plot_residuals, plot_aic_comparison
    7. write_results(results.json)
    8. print summary table to stdout
    """
```

---

## Pseudo-code: main() flow

```
LOG: "H-M2 AIC Model Comparison starting"

t_glue, y_glue = load_timeseries("../h-e1/code/data/glue_timeseries_clean.csv")
t_sg,   y_sg   = load_timeseries("../h-e1/code/data/superglue_timeseries_clean.csv")
LOG: f"GLUE n={len(t_glue)}, SuperGLUE n={len(t_sg)}"

for name, t, y in [("glue", t_glue, y_glue), ("superglue", t_sg, y_sg)]:
    log_fit  = fit_logistic(t, y)     # reused from H-E1
    lin_fit  = fit_linear(t, y)       # reused from H-E1
    pl_fit   = fit_power_law(t, y)    # new

    if not log_fit["converged"]:
        RAISE RuntimeError(f"Logistic fit failed for {name}")

    results[name] = {
        "aic_logistic": log_fit["aic"],
        "aic_linear":   lin_fit["aic"],
        "aic_power":    pl_fit["aic"],
        "delta_log_vs_lin": compute_delta_aic(log_fit, lin_fit),
        "delta_log_vs_pl":  compute_delta_aic(log_fit, pl_fit),
        "logistic_params":  dict(zip(["K","r","t0"], log_fit["popt"])),
    }
    LOG: f"{name}: AIC log={log_fit['aic']:.2f}, lin={lin_fit['aic']:.2f}, pl={pl_fit['aic']:.2f}"
    LOG: f"{name}: Δ(log-lin)={results[name]['delta_log_vs_lin']:.2f}, Δ(log-pl)={results[name]['delta_log_vs_pl']:.2f}"

gate_pass, indicators = verify_gate(results)
LOG: f"GATE: {'PASS' if gate_pass else 'FAIL'} — {indicators}"

figures_dir = Path("../figures")
figures_dir.mkdir(parents=True, exist_ok=True)
plot_gate_metrics(results, figures_dir)
plot_model_fits({"glue": (t_glue, y_glue), "superglue": (t_sg, y_sg)},
                {"glue": {...}, "superglue": {...}}, figures_dir)
plot_residuals(..., figures_dir)
plot_aic_comparison(results, figures_dir)

write_results(results, (gate_pass, indicators), Path("../results.json"))
PRINT summary table
```

---

## Subtask Details (Budget: 2)

### L-5-1: Gate Metrics Bar Chart
- **Parent:** A-5 (Figures, complexity 9)
- **Scope:** `plot_gate_metrics()` implementation
- Details: 2-group bar chart (GLUE, SuperGLUE), 2 bars each (Δlog-lin, Δlog-pl), red threshold lines at y=-4 and y=-2, color-coded pass/fail bars

### L-5-2: Model Fit Overlay + Residual Plots
- **Parent:** A-5 (Figures, complexity 9)
- **Scope:** `plot_model_fits()` + `plot_residuals()` implementation
- Details: 2-subplot figure; scatter dots + 3 smooth curve overlays each; R² in legend; residual subplots show systematic deviation in plateau region for linear/power-law

---

## AIC Formula Reference

```
AIC = n * log(RSS/n) + 2k
where:
  n   = number of data points
  RSS = sum of squared residuals
  k   = number of free parameters (logistic=3, linear=2, power_law=2)

ΔAIC = AIC_logistic - AIC_linear
  < -4  → logistic substantially preferred (Burnham & Anderson 2002 criterion)
  < -2  → logistic preferred (moderate evidence)
  > 0   → linear/power preferred (logistic fails gate)
```
