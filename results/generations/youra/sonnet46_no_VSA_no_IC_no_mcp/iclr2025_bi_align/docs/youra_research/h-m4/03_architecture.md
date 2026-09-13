# Architecture Document: H-M4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 — Cross-dataset OLS Replication (Gao et al. 2023)
**Phase:** 3 — Implementation Planning

---

## 1. System Overview

H-M4 is a pure statistical pipeline — no neural network, no GPU, no training loop. The architecture mirrors H-M3 exactly with one change: input CSV path points to Gao et al. 2023 digitized data instead of Coste et al. data. Code reuse is maximal; the only new module is `data_loader.py` adapted for `gao_2023_gap.csv`.

```
[Manual Step] WebPlotDigitizer digitization
       ↓
gao_2023_raw.csv → [preprocess.py] → gao_2023_gap.csv
                                           ↓
                               [regression.py] fit_ols_regression()
                                           ↓
                               [gate.py] check_gate() + compare_with_coste()
                                           ↓
                               [verify.py] verify_mechanism_activated()
                                           ↓
                               [figures.py] generate 5 figures
                                           ↓
                               [main.py] save results JSON + print summary
```

---

## 2. Directory Structure

```
docs/youra_research/h-m4/
├── data/
│   ├── gao_2023_raw.csv          # Phase 4 digitization output
│   └── gao_2023_gap.csv          # Phase 4 preprocessing output
├── code/
│   ├── config.py                 # All configurable paths/params
│   ├── main.py                   # Entry point
│   └── src/
│       ├── preprocess.py         # Normalization + gap computation
│       ├── regression.py         # OLS pipeline (reused from H-M3)
│       ├── gate.py               # check_gate + compare_with_coste
│       ├── verify.py             # verify_mechanism_activated
│       └── figures.py            # 5 figure generators
├── figures/                      # PNG outputs
├── results/
│   ├── h_m4_results.json         # All metrics + gate outcome
│   └── gao_2023_gap_final.csv    # Final processed data copy
└── 04_validation.md              # Phase 4 report (generated)
```

---

## 3. Module Specifications

### 3.1 `config.py`

Single source of truth for all paths and parameters.

```python
from pathlib import Path

BASE = Path("docs/youra_research/h-m4")
DATA_DIR = BASE / "data"
RESULTS_DIR = BASE / "results"
FIGURES_DIR = BASE / "figures"
CODE_DIR = BASE / "code"

DATA_RAW = DATA_DIR / "gao_2023_raw.csv"
DATA_GAP = DATA_DIR / "gao_2023_gap.csv"
RESULTS_JSON = RESULTS_DIR / "h_m4_results.json"
RESULTS_CSV = RESULTS_DIR / "gao_2023_gap_final.csv"

# H-M3 reference values for cross-dataset comparison
BETA_COSTE = 0.1433
R2_COSTE = 0.9577
P_COSTE = 8.89e-7
N_COSTE = 10

# Bootstrap
N_BOOT = 10_000
SEED = 42

# Gate (SHOULD_WORK)
GATE_BETA_MIN = 0.0
GATE_P_MAX = 0.05
MIN_N = 6
```

### 3.2 `src/preprocess.py`

Load raw digitized CSV; apply normalization; compute gap; validate; save gap CSV.

```python
import numpy as np
import pandas as pd
from pathlib import Path

def load_raw(data_raw_path: str | Path) -> pd.DataFrame:
    assert Path(data_raw_path).exists(), f"Raw data not found: {data_raw_path}. Complete WebPlotDigitizer step first."
    df = pd.read_csv(data_raw_path)
    assert {"kl_budget", "proxy_raw", "gold_raw"}.issubset(df.columns), "Missing columns in raw CSV"
    assert len(df) >= 6, f"N={len(df)} insufficient (min 6 for valid regression)"
    assert not df.isnull().any().any(), "NaN detected in raw data — re-digitize"
    return df

def normalize(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())

def compute_gap(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["proxy_norm"] = normalize(df["proxy_raw"])
    df["gold_norm"] = normalize(df["gold_raw"])
    df["gap"] = df["proxy_norm"] - df["gold_norm"]
    assert df["gap"].std() > 0.01, "Gap has near-zero variance — normalization error, check proxy/gold curves"
    return df

def validate_gap(df: pd.DataFrame) -> None:
    assert not df.isnull().any().any(), "NaN in processed data"
    kl = df["kl_budget"].values
    assert all(kl[i] <= kl[i+1] for i in range(len(kl)-1)), "kl_budget not monotonically non-decreasing"

def save_gap(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df[["kl_budget", "proxy_norm", "gold_norm", "gap"]].to_csv(path, index=False)
```

### 3.3 `src/regression.py`

Identical to H-M3 — reused verbatim. OLS + bootstrap CI.

```python
import numpy as np
from scipy import stats
import statsmodels.api as sm

def fit_ols_regression(kl_values: np.ndarray, gap_values: np.ndarray, n_boot: int = 10_000, seed: int = 42) -> dict:
    slope, intercept, r_value, p_value, std_err = stats.linregress(kl_values, gap_values)
    r_squared = r_value ** 2
    t_stat = slope / std_err

    X = sm.add_constant(kl_values)
    model = sm.OLS(gap_values, X).fit()
    ci_low, ci_high = model.conf_int(alpha=0.05)[1]

    rng = np.random.default_rng(seed)
    idx = np.arange(len(kl_values))
    boot_slopes = [
        stats.linregress(kl_values[rng.choice(idx, size=len(idx), replace=True)], gap_values[rng.choice(idx, size=len(idx), replace=True)])[0]
        for _ in range(n_boot)
    ]
    boot_ci = np.percentile(boot_slopes, [2.5, 97.5])

    return {
        "slope": float(slope), "intercept": float(intercept),
        "r_squared": float(r_squared), "p_value": float(p_value),
        "std_err": float(std_err), "t_stat": float(t_stat),
        "ci_parametric": [float(ci_low), float(ci_high)],
        "ci_bootstrap": boot_ci.tolist(),
        "n": int(len(kl_values))
    }
```

**Note:** Bootstrap resamples both kl and gap indices jointly — this is the H-M3 protocol. Maintains paired structure.

### 3.4 `src/gate.py`

Gate evaluation + cross-dataset comparison.

```python
def check_gate(results: dict, beta_min: float = 0.0, p_max: float = 0.05) -> dict:
    gate_pass = (results["slope"] > beta_min) and (results["p_value"] < p_max)
    reason = []
    if results["slope"] <= beta_min:
        reason.append(f"β={results['slope']:.4f} not > {beta_min}")
    if results["p_value"] >= p_max:
        reason.append(f"p={results['p_value']:.4f} not < {p_max}")
    return {
        "gate_pass": gate_pass,
        "gate_type": "SHOULD_WORK",
        "reason": "All conditions met" if gate_pass else "; ".join(reason)
    }

def compare_with_coste(beta_gao: float, beta_coste: float = 0.1433) -> dict:
    ratio = beta_gao / beta_coste if beta_coste != 0 else float("inf")
    within_order = 0.1 <= abs(ratio) <= 10.0
    return {
        "beta_gao": beta_gao, "beta_coste": beta_coste,
        "ratio": ratio, "within_order_of_magnitude": within_order
    }
```

### 3.5 `src/verify.py`

Mechanism activation verification.

```python
import numpy as np
from pathlib import Path

def verify_mechanism_activated(results: dict, data_path: str) -> tuple[bool, dict]:
    indicators = {
        "data_file_exists": Path(data_path).exists(),
        "n_sufficient": results.get("n", 0) >= 6,
        "slope_computed": results.get("slope") is not None and not np.isnan(results["slope"]),
        "p_value_valid": 0.0 <= results.get("p_value", 1.0) <= 1.0,
        "r_squared_valid": 0.0 <= results.get("r_squared", -1.0) <= 1.0,
        "ci_computed": results.get("ci_bootstrap") is not None,
    }
    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    return True, indicators
```

### 3.6 `src/figures.py`

5 figure generators. All saved as PNG to `docs/youra_research/h-m4/figures/`.

**fig1_gate_metrics:** Bar chart — β and p vs thresholds; H-M3 reference bars
**fig2_regression_gao:** Scatter + OLS line + 95% CI band; annotate β, R², p
**fig3_cross_dataset_slopes:** Side-by-side β_Coste vs β_Gao with error bars
**fig4_dual_overlay:** Both datasets on one plot with respective regression lines
**fig5_bootstrap_histogram:** Histogram of 10k bootstrap slopes; mark β and 95% CI

### 3.7 `main.py`

Entry point: orchestrates all steps in order, handles gate FAIL gracefully.

```python
def main():
    # 1. Load and preprocess
    df_raw = load_raw(config.DATA_RAW)
    df_gap = compute_gap(df_raw)
    validate_gap(df_gap)
    save_gap(df_gap, config.DATA_GAP)

    kl = df_gap["kl_budget"].values
    gap = df_gap["gap"].values

    # 2. OLS regression
    results = fit_ols_regression(kl, gap, n_boot=config.N_BOOT, seed=config.SEED)
    print(f"Gao OLS regression fitted: slope={results['slope']:.4f}, p={results['p_value']:.2e}, R2={results['r_squared']:.4f}")

    # 3. Gate + cross-dataset comparison
    gate = check_gate(results)
    comparison = compare_with_coste(results["slope"])
    print(f"β_Gao/β_Coste ratio: {comparison['ratio']:.3f} (within order of magnitude: {comparison['within_order_of_magnitude']})")
    print(f"Gate (SHOULD_WORK): {'PASS' if gate['gate_pass'] else 'FAIL'} — {gate['reason']}")

    # 4. Mechanism verification
    verify_mechanism_activated(results, str(config.DATA_GAP))

    # 5. Figures
    generate_all_figures(df_gap, results, gate, comparison, config.FIGURES_DIR)

    # 6. Save results
    save_results(results, gate, comparison, config)

if __name__ == "__main__":
    main()
```

---

## 4. Data Flow

```
gao_2023_raw.csv (N≈8-10 rows: kl_budget, proxy_raw, gold_raw)
    → preprocess.py → gao_2023_gap.csv (adds proxy_norm, gold_norm, gap)
    → regression.py → results dict (slope, p, R², CI×2, N)
    → gate.py → gate dict (pass/fail, reason) + comparison dict
    → verify.py → indicator dict (all True or RuntimeError)
    → figures.py → 5 PNG files
    → main.py → h_m4_results.json + stdout summary
```

---

## 5. Dependency Versions

| Library | Min Version | Purpose |
|---------|-------------|---------|
| Python | 3.10 | Runtime |
| scipy | 1.10 | stats.linregress |
| statsmodels | 0.14 | OLS, conf_int |
| numpy | 1.24 | Array ops |
| matplotlib | 3.7 | Figures |
| pandas | 2.0 | CSV I/O |

Environment: clone `youra-h-m3` conda env or reuse directly (same dependencies).

---

## 6. H-M3 Reuse Map

| Component | H-M3 Source | H-M4 Change |
|-----------|-------------|-------------|
| `regression.py` | h-m3/code/src/regression.py | None — reused verbatim |
| `gate.py` | h-m3/code/src/gate.py | compare_with_coste() added |
| `verify.py` | h-m3/code/src/verify.py | None — reused verbatim |
| `config.py` | h-m3/code/config.py | Paths updated to h-m4; BETA_COSTE added |
| `preprocess.py` | h-m3/code/src/preprocess.py | Reads gao_2023_raw.csv instead of h-m2 CSV |
| `figures.py` | h-m3/code/src/figures.py | fig3/fig4 added for cross-dataset |
| `main.py` | h-m3/code/main.py | compare_with_coste() call added |
