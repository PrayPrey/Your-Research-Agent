# Logic Design: H-M3 — Parameter Extraction & Plausibility Validation

**Applied:** Standard scipy pcov→perr→CI95 extraction pattern
**Applied:** Residual bootstrap CI fallback pattern (500 resamples)
**Applied:** Dataclass-based result container pattern

---

## Codebase Analysis (Serena)

### H-M2 Actual Code: `/docs/youra_research/h-m2/code/run.py`

Verified function signatures from actual code:

```python
# fit_logistic — ACTUAL SIGNATURE (run.py line ~41)
def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict:
    # Returns dict with keys: popt, pcov, r2, aic, ci95, converged
    # popt: np.ndarray shape (3,) — [K, r, t0]
    # pcov: np.ndarray shape (3,3) — covariance matrix
    # ci95: np.ndarray shape (3,) — 1.96 * sqrt(diag(pcov))
    # converged: bool

# logistic — ACTUAL SIGNATURE (run.py line ~31)
def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    exponent = np.clip(-r * (t - t0), -500, 500)
    return K / (1.0 + np.exp(exponent))

# _r2_aic — ACTUAL SIGNATURE (run.py line ~21)
def _r2_aic(y: np.ndarray, y_pred: np.ndarray, k: int) -> Tuple[float, float]:
    # Returns (r2, aic)
```

**Key finding:** `fit_logistic` already returns `pcov` and `ci95` in its result dict. H-M3 calls `fit_logistic` and extracts from the returned dict — no re-implementation needed.

**Import path for H-M3:**
```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m2" / "code"))
from run import fit_logistic, logistic, _r2_aic
```

---

## External Dependencies API

### From h-m2/code/run.py (verified)

| Function | Signature | Returns |
|----------|-----------|---------|
| `fit_logistic` | `(t: np.ndarray, y: np.ndarray) -> dict` | `{popt:(3,), pcov:(3,3), r2:float, aic:float, ci95:(3,), converged:bool}` |
| `logistic` | `(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray` | `(N,)` predictions |
| `_r2_aic` | `(y: np.ndarray, y_pred: np.ndarray, k: int) -> Tuple[float, float]` | `(r2, aic)` |

**Bounds used in H-M2 fit_logistic (actual code):**
- K: [0.8, 1.05], r: [0.01, 5.0], t0: [-20, 60]
- p0: [0.9, 0.5, median(t)*0.3]

---

## DataClass Definitions

```python
from dataclasses import dataclass, field
from typing import Dict, Optional
import numpy as np

@dataclass
class PlausibilityFlags:
    K_in_range: bool        # 0.85 <= K <= 1.0
    r_positive: bool        # r > 0
    t0_in_range: bool       # 6 <= t0_absolute <= 48
    ci_t0_narrow: bool      # 2 * 1.96 * perr[2] < 12.0
    all_pass: bool = field(init=False)

    def __post_init__(self):
        self.all_pass = all([self.K_in_range, self.r_positive,
                             self.t0_in_range, self.ci_t0_narrow])

@dataclass
class ParamResult:
    benchmark: str           # "glue" | "superglue"
    K: float                 # asymptote/ceiling
    r: float                 # growth rate
    t0_relative: float       # inflection point relative to fit origin (months)
    t0_absolute: float       # t0_relative + release_offset (months since release)
    perr: np.ndarray         # shape (3,) — 1-sigma std errors [K_err, r_err, t0_err]
    ci_95: np.ndarray        # shape (3,) — 1.96 * perr
    pcov_finite: bool        # True if pcov diagonal has no inf
    ci_source: str           # "pcov" | "bootstrap"
    flags: PlausibilityFlags
    mechanism_ok: bool       # True if verify_mechanism_activated passes

@dataclass
class BenchmarkData:
    name: str                # "glue" | "superglue"
    t: np.ndarray            # shape (N,) months since release
    y: np.ndarray            # shape (N,) normalized scores in [0,1]
    release_offset: float    # = 0 (t=0 already IS benchmark release in H-M2 data)
```

---

## Subtask APIs

### L-3-1: `extract_params`

```python
def extract_params(
    t_data: np.ndarray,        # shape (N,) — months since release (t=0 = release)
    y_data: np.ndarray,        # shape (N,) — normalized scores [0,1]
    benchmark_name: str,       # "glue" | "superglue"
    release_offset: float = 0.0  # = 0 (H-M2 data already uses release as t=0)
) -> ParamResult:
    """
    Calls h-m2's fit_logistic, extracts parameters, computes CI, checks plausibility.
    Falls back to bootstrap CI if pcov diagonal contains inf.
    """
    fit = fit_logistic(t_data, y_data)  # from h-m2/code/run.py
    if not fit["converged"]:
        raise RuntimeError(f"fit_logistic did not converge for {benchmark_name}")

    popt = fit["popt"]         # shape (3,) — [K, r, t0_relative]
    pcov = fit["pcov"]         # shape (3,3)

    pcov_finite = check_pcov_validity(pcov)
    if pcov_finite:
        perr = np.sqrt(np.diag(pcov))   # shape (3,)
        ci_95 = 1.96 * perr             # shape (3,)
        ci_source = "pcov"
    else:
        ci_bounds = bootstrap_ci(t_data, y_data)  # shape (3,2)
        ci_95 = (ci_bounds[:, 1] - ci_bounds[:, 0]) / 2  # half-width
        perr = ci_95 / 1.96
        ci_source = "bootstrap"

    K, r, t0_relative = popt[0], popt[1], popt[2]
    t0_absolute = t0_relative + release_offset  # = t0_relative + 0

    flags = PlausibilityFlags(
        K_in_range=(0.85 <= K <= 1.0),
        r_positive=(r > 0),
        t0_in_range=(6.0 <= t0_absolute <= 48.0),
        ci_t0_narrow=(2 * ci_95[2] < 12.0),
    )

    mech_ok, _ = verify_mechanism_activated(popt, pcov)

    return ParamResult(
        benchmark=benchmark_name, K=K, r=r,
        t0_relative=t0_relative, t0_absolute=t0_absolute,
        perr=perr, ci_95=ci_95,
        pcov_finite=pcov_finite, ci_source=ci_source,
        flags=flags, mechanism_ok=mech_ok,
    )
```

### L-3-2: `verify_mechanism_activated`

```python
def verify_mechanism_activated(
    popt: np.ndarray,   # shape (3,)
    pcov: np.ndarray,   # shape (3,3)
) -> Tuple[bool, Dict[str, bool]]:
    """Checks that the parameter extraction mechanism is properly activated."""
    indicators = {
        "popt_shape_correct": popt.shape == (3,),
        "pcov_finite":        np.all(np.isfinite(np.diag(pcov))),
        "K_extracted":        0.0 < popt[0] < 1.1,
        "r_extracted":        popt[1] != 0.0,
        "t0_extracted":       not np.isnan(popt[2]),
        "ci_computed":        np.all(np.sqrt(np.diag(pcov)) > 0) if np.all(np.isfinite(np.diag(pcov))) else True,
    }
    return all(indicators.values()), indicators
```

### L-4-1: `bootstrap_ci`

```python
def bootstrap_ci(
    t_data: np.ndarray,      # shape (N,)
    y_data: np.ndarray,      # shape (N,)
    n_resamples: int = 500,
    confidence: float = 0.95,
    random_seed: int = 42,
) -> np.ndarray:             # shape (3,2) — [lower, upper] per param [K, r, t0]
    """
    Residual bootstrap CI for logistic parameters.
    Triggered only when pcov diagonal contains inf.

    Pseudo-code:
    1. Fit logistic to original data → popt_orig, y_hat
    2. Compute residuals: resid = y_data - y_hat  # shape (N,)
    3. For i in range(n_resamples):
         resid_boot = resample(resid, replace=True)  # shape (N,)
         y_boot = y_hat + resid_boot                 # shape (N,)
         fit_boot = fit_logistic(t_data, y_boot)
         if fit_boot["converged"]: collect popt_boot
    4. ci_lower = np.percentile(boot_params, (1-confidence)/2 * 100, axis=0)  # (3,)
    5. ci_upper = np.percentile(boot_params, (1+confidence)/2 * 100, axis=0)  # (3,)
    6. return np.stack([ci_lower, ci_upper], axis=1)  # (3,2)
    """
    rng = np.random.default_rng(random_seed)
    fit_orig = fit_logistic(t_data, y_data)
    y_hat = logistic(t_data, *fit_orig["popt"])  # shape (N,)
    residuals = y_data - y_hat                    # shape (N,)

    boot_params = []
    for _ in range(n_resamples):
        idx = rng.integers(0, len(residuals), size=len(residuals))
        y_boot = y_hat + residuals[idx]
        fit_boot = fit_logistic(t_data, y_boot)
        if fit_boot["converged"]:
            boot_params.append(fit_boot["popt"])  # (3,)

    boot_arr = np.array(boot_params)              # (M,3) where M <= n_resamples
    alpha = (1 - confidence) / 2
    ci_lower = np.percentile(boot_arr, alpha * 100, axis=0)        # (3,)
    ci_upper = np.percentile(boot_arr, (1 - alpha) * 100, axis=0)  # (3,)
    return np.stack([ci_lower, ci_upper], axis=1)                   # (3,2)
```

### L-4-2: `check_pcov_validity`

```python
def check_pcov_validity(pcov: np.ndarray) -> bool:  # shape (3,3) in
    """Returns True if pcov diagonal is fully finite (no inf, no nan)."""
    return bool(np.all(np.isfinite(np.diag(pcov))))
```

### L-6-1: `plot_gate_metrics_comparison`

```python
def plot_gate_metrics_comparison(
    results_glue: ParamResult,
    results_superglue: ParamResult,
    output_dir: Path,
) -> Path:
    """
    Mandatory figure (FR-7.1): Bar chart of K, r, t0_absolute for both benchmarks
    with threshold bound lines overlaid.

    Layout: 3 subplots (one per parameter), each with 2 bars (GLUE, SuperGLUE)
    and horizontal lines at threshold boundaries.
    Returns: output_dir / "gate_metrics_comparison.png"

    Pseudo-code:
    fig, axes = plt.subplots(1, 3)
    for i, (param, label, bounds) in enumerate([
        ("K", "Ceiling K", (0.85, 1.0)),
        ("r", "Growth Rate r", (0.0, None)),
        ("t0_absolute", "Inflection t0 (months)", (6, 48)),
    ]):
        ax = axes[i]
        vals = [getattr(results_glue, param), getattr(results_superglue, param)]
        ax.bar(["GLUE", "SuperGLUE"], vals, color=["#4C72B0", "#DD8452"])
        ax.axhline(bounds[0], color="red", linestyle="--", label=f"min={bounds[0]}")
        if bounds[1]: ax.axhline(bounds[1], color="red", linestyle="--", label=f"max={bounds[1]}")
        ax.set_title(label)
    out = output_dir / "gate_metrics_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    return out
    """
    ...  # implementation as above pseudo-code
```

### L-6-2: `plot_parameter_ci`

```python
def plot_parameter_ci(
    results_glue: ParamResult,
    results_superglue: ParamResult,
    output_dir: Path,
) -> Path:
    """
    Figure (FR-7.2): Error bar plot for K, r, t0_absolute with 95% CI bands.

    Layout: 3 subplots, each with 2 points (GLUE, SuperGLUE) + error bars (ci_95)
    Returns: output_dir / "parameter_ci.png"

    Pseudo-code:
    fig, axes = plt.subplots(1, 3)
    for i, (attr, err_idx, label) in enumerate([
        ("K", 0, "K (ceiling)"),
        ("r", 1, "r (growth rate)"),
        ("t0_absolute", 2, "t0_abs (months)"),
    ]):
        ax = axes[i]
        vals = [getattr(r, attr) for r in [results_glue, results_superglue]]
        errs = [r.ci_95[err_idx] for r in [results_glue, results_superglue]]
        ax.errorbar([0, 1], vals, yerr=errs, fmt="o", capsize=5)
        ax.set_xticks([0,1]); ax.set_xticklabels(["GLUE", "SuperGLUE"])
        ax.set_title(label)
    out = output_dir / "parameter_ci.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    return out
    """
    ...
```

---

## Supporting Functions

### `check_plausibility`

```python
def check_plausibility(result: ParamResult) -> PlausibilityFlags:
    """Re-evaluates plausibility from ParamResult (convenience wrapper)."""
    return result.flags
```

### `write_results`

```python
def write_results(
    results: Dict[str, ParamResult],   # {"glue": ..., "superglue": ...}
    output_path: Path,
    gate_pass: bool,
) -> None:
    """Serializes ParamResult dicts to JSON. numpy arrays → lists."""
    payload = {
        bname: {
            "K": r.K, "r": r.r,
            "t0_relative": r.t0_relative,
            "t0_absolute": r.t0_absolute,
            "perr": r.perr.tolist(),
            "ci_95": r.ci_95.tolist(),
            "ci_source": r.ci_source,
            "pcov_finite": r.pcov_finite,
            "flags": {
                "K_in_range": r.flags.K_in_range,
                "r_positive": r.flags.r_positive,
                "t0_in_range": r.flags.t0_in_range,
                "ci_t0_narrow": r.flags.ci_t0_narrow,
                "all_pass": r.flags.all_pass,
            },
            "mechanism_ok": r.mechanism_ok,
        }
        for bname, r in results.items()
    }
    payload["gate_pass"] = gate_pass
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
```

---

## Main Orchestration Pseudo-code (run.py)

```python
def main():
    # 1. Load data (reuse H-M2 pipeline)
    glue_data = load_timeseries("glue")      # BenchmarkData(t:(N,), y:(N,))
    superglue_data = load_timeseries("superglue")

    figures_dir = Path("h-m3/figures"); figures_dir.mkdir(parents=True, exist_ok=True)
    results_path = Path("h-m3/results.json")

    # 2. Extract parameters for each benchmark
    result_glue = extract_params(glue_data.t, glue_data.y, "glue", release_offset=0.0)
    result_superglue = extract_params(superglue_data.t, superglue_data.y, "superglue", release_offset=0.0)

    # 3. Handle t0 border case (FR-4.9 / A-8)
    for res in [result_glue, result_superglue]:
        if not res.flags.t0_in_range:
            logging.warning(f"{res.benchmark}: t0_absolute={res.t0_absolute:.2f} outside [6,48]. "
                            f"Relaxed threshold [0,48]: {0 <= res.t0_absolute <= 48}")

    # 4. Gate verdict
    gate_pass = result_glue.flags.all_pass and result_superglue.flags.all_pass

    # 5. Visualize
    plot_gate_metrics_comparison(result_glue, result_superglue, figures_dir)
    plot_parameter_ci(result_glue, result_superglue, figures_dir)

    # 6. Save results
    write_results({"glue": result_glue, "superglue": result_superglue}, results_path, gate_pass)

    # 7. Print summary + exit
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    sys.exit(0 if gate_pass else 1)
```
