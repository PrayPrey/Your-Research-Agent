# Logic: H-M1
# Cox Proportional Hazards — Diversity Predictor Significance Test

**Date:** 2026-08-03
**Phase:** 3 — Implementation Planning

Applied: statistical-estimation-pipeline (no training loop, deterministic MLE)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `GateResult` dataclass — gate, passed, value, threshold, message
- `GateValidator.run_all(stats_df, panel, n_matched, enriched_panel)` — fail-fast gate pattern
- `main()` in `run.py` — step-by-step orchestration with json.dump results pattern
- `H1Config` / `FigureConfig` dataclasses — config pattern replicated in H-M1

H-M1 does NOT import H-E1 at runtime. Consumes output CSV only.

---

## External Dependencies API

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class H1Config:
    output_csv: str = "h_e2_panel_with_diversity.csv"  # ← H-M1 reads this file

@dataclass
class FigureConfig:
    dpi: int = 150
    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"
    fname_gate_metrics: str = "gate_metrics.png"

# From: docs/youra_research/h-e1/code/gates.py (ACTUAL CODE)
@dataclass
class GateResult:
    gate: str
    passed: bool
    value: float
    threshold: float
    message: str

# From: docs/youra_research/h-e1/code/run.py (ACTUAL CODE)
# Pattern: step-by-step orchestration, json.dump with indent=2
# results_path = hyp_dir / "experiment_results.json"
# with open(str(results_path), "w") as f:
#     json.dump(experiment_results, f, indent=2)
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

Column names confirmed in `gates.py` VIFChecker.COVARIATES:
- `"log_unique_paper_count_at_intro_z"` — primary diversity predictor
- `"task_age"`, `"log_publication_volume"`, `"benchmark_introduction_year"` — controls

---

## A-3: Model Fitting [Complexity: 10, Budget: 2 subtasks]

Applied: statistical-estimation-pipeline

### API Signatures

```python
import warnings
from typing import Tuple
from lifelines import CoxPHFitter
import pandas as pd
from config import CoxConfig


def fit_models(
    panel_df: pd.DataFrame,
    cfg: CoxConfig,
) -> Tuple[CoxPHFitter, CoxPHFitter]:
    """Fit M0 (controls) and M1 (controls + diversity). Returns (M0, M1)."""
    ...
```

### Pseudo-code

```
def fit_models(panel_df, cfg):
    base_cols = list(cfg.base_covariates) + [cfg.duration_col, cfg.event_col]
    full_cols  = base_cols + [cfg.diversity_col]

    def _fit(fitter, cols, label):
        df_sub = panel_df[cols].dropna()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fitter.fit(df_sub, duration_col=cfg.duration_col, event_col=cfg.event_col)
            converged = not any("ConvergenceWarning" in str(x.category) for x in w)
        if not converged:
            print(f"WARNING: {label} convergence issue — refitting penalizer={cfg.penalizer_fallback}")
            fitter2 = CoxPHFitter(penalizer=cfg.penalizer_fallback)
            fitter2.fit(df_sub, duration_col=cfg.duration_col, event_col=cfg.event_col)
            return fitter2
        return fitter

    M0 = _fit(CoxPHFitter(penalizer=cfg.penalizer), base_cols, "M0")
    print(f"M0 fitted: log_likelihood={M0.log_likelihood_:.4f}")

    M1 = _fit(CoxPHFitter(penalizer=cfg.penalizer), full_cols, "M1")
    print(f"M1 fitted: log_likelihood={M1.log_likelihood_:.4f}, concordance={M1.concordance_index_:.4f}")

    return M0, M1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | _fit inner function | warnings.catch_warnings loop, ConvergenceWarning detection, penalizer fallback refit |
| L-3-2 | M0 / M1 sequential fit | Column subset selection, dropna, logging |

---

## A-4: LRT + HR Extraction [Complexity: 12, Budget: 2 subtasks]

Applied: statistical-estimation-pipeline

### API Signatures

```python
from dataclasses import dataclass
from lifelines import CoxPHFitter
from scipy import stats
import numpy as np
from config import CoxConfig


@dataclass
class LRTResult:
    lrt_stat: float
    p_value: float
    HR: float
    CI_lower: float
    CI_upper: float
    abs_effect: float
    concordance: float
    M0_log_likelihood: float
    M1_log_likelihood: float
    direction: str       # "H1" | "H2" | "H0"
    gate_passed: bool


def run_lrt(
    M0: CoxPHFitter,
    M1: CoxPHFitter,
    cfg: CoxConfig,
) -> LRTResult:
    """LRT chi2(df=1), HR/CI extraction, gate eval, direction routing."""
    ...
```

### Tensor Shapes (key variable types)

| Variable | Type/Shape | Note |
|----------|-----------|------|
| `M1.hazard_ratios_` | pd.Series, index=covariate names | `.loc[diversity_col]` → scalar |
| `M1.confidence_intervals_` | pd.DataFrame, index=covariate names, cols=["lower 0.95","upper 0.95"] | log-scale; must exp() |
| `lrt_stat` | float | must be >= 0 |
| `p_value` | float | chi2.sf output |

### Pseudo-code

```
def run_lrt(M0, M1, cfg):
    ll0 = M0.log_likelihood_
    ll1 = M1.log_likelihood_

    # Edge case: non-finite log-likelihoods
    if not (np.isfinite(ll0) and np.isfinite(ll1)):
        raise ValueError(f"Non-finite log-likelihoods: M0={ll0}, M1={ll1}")

    lrt_stat = -2.0 * (ll0 - ll1)

    # Edge case: negative lrt_stat (M1 worse — L2 penalty can cause this)
    if lrt_stat < 0:
        print(f"WARNING: lrt_stat={lrt_stat:.6f} < 0; M1 not better than M0 under L2 penalty")
        lrt_stat = max(lrt_stat, 0.0)  # clip to 0 for chi2.sf

    p_value = stats.chi2.sf(lrt_stat, df=cfg.lrt_df)
    print(f"LRT stat={lrt_stat:.4f}, p={p_value:.4f}")

    # HR extraction
    HR = float(M1.hazard_ratios_[cfg.diversity_col])
    CI_lower = float(np.exp(M1.confidence_intervals_.loc[cfg.diversity_col, "lower 0.95"]))
    CI_upper = float(np.exp(M1.confidence_intervals_.loc[cfg.diversity_col, "upper 0.95"]))
    abs_effect = abs(HR - 1.0)
    print(f"HR={HR:.4f}, CI=[{CI_lower:.4f}, {CI_upper:.4f}], |HR-1|={abs_effect:.4f}")

    # Gate
    gate_passed = (p_value < cfg.p_threshold) and (abs_effect >= cfg.hr_effect_threshold)

    # Direction (pre-specified)
    if p_value < cfg.p_threshold and HR < 1.0:
        direction = "H1"   # breadth → resistance
    elif p_value < cfg.p_threshold and HR > 1.0:
        direction = "H2"   # saturation → replacement
    else:
        direction = "H0"   # null

    return LRTResult(
        lrt_stat=lrt_stat, p_value=p_value,
        HR=HR, CI_lower=CI_lower, CI_upper=CI_upper,
        abs_effect=abs_effect,
        concordance=M1.concordance_index_,
        M0_log_likelihood=ll0, M1_log_likelihood=ll1,
        direction=direction, gate_passed=gate_passed,
    )
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | LRT computation | ll finiteness check, lrt_stat, negative-stat guard, chi2.sf |
| L-4-2 | HR/CI extraction + gate + direction | hazard_ratios_ / confidence_intervals_ indexing, exp(), gate bool, H1/H2/H0 routing |

---

## A-12: Integration run.py [Complexity: 8, Budget: 1 subtask]

Applied: statistical-estimation-pipeline

### API Signatures

```python
from pathlib import Path
import json
from datetime import datetime, timezone
from config import CFG, FIG_CFG
from cox_analysis import load_panel, fit_models, run_lrt, run_diagnostics
from visualization import save_all_figures


def main() -> None:
    """Orchestrate: load → fit → lrt → diagnostics → figures → serialize → print."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
def main():
    code_dir = Path(__file__).parent
    hyp_dir  = code_dir.parent

    print("=" * 60)
    print("H-M1: Cox PH Diversity Significance Test")
    print("=" * 60)

    # 1. Load panel
    try:
        panel_df = load_panel(CFG)
    except FileNotFoundError as e:
        print(f"ERROR: Panel CSV not found — run H-E1 first.\n{e}")
        raise SystemExit(1)

    # 2. Fit M0 / M1
    M0, M1 = fit_models(panel_df, CFG)

    # 3. LRT — assert M1 >= M0 (post lrt, before gate)
    result = run_lrt(M0, M1, CFG)
    assert result.M1_log_likelihood >= result.M0_log_likelihood, (
        f"M1.ll={result.M1_log_likelihood:.4f} < M0.ll={result.M0_log_likelihood:.4f}"
    )

    # 4. Diagnostics
    diag = run_diagnostics(M1, panel_df)
    print(f"Concordance: {diag['concordance']:.4f}")
    if diag['ph_violations']:
        print(f"PH assumption violations: {diag['ph_violations']}")

    # 5. Figures
    figures_dir = hyp_dir / CFG.figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)
    saved_figs = save_all_figures(M1, panel_df, result, CFG, FIG_CFG)

    # 6. Serialize
    results_path = hyp_dir / "experiment_results.json"
    payload = {
        "hypothesis_id": "H-M1",
        "gate_passed": result.gate_passed,
        "lrt_stat": result.lrt_stat,
        "p_value": result.p_value,
        "HR": result.HR,
        "CI_lower": result.CI_lower,
        "CI_upper": result.CI_upper,
        "abs_effect": result.abs_effect,
        "concordance_M1": result.concordance,
        "M0_log_likelihood": result.M0_log_likelihood,
        "M1_log_likelihood": result.M1_log_likelihood,
        "direction": result.direction,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(str(results_path), "w") as f:
        json.dump(payload, f, indent=2)

    # 7. Print summary
    gate_str = "PASS" if result.gate_passed else "FAIL (meaningful null)"
    print("\n" + "=" * 60)
    print(f"H-M1 GATE: {gate_str}")
    print(f"  direction={result.direction}, p={result.p_value:.4f}, HR={result.HR:.4f}, |HR-1|={result.abs_effect:.4f}")
    print(f"  Results: {results_path}")
    print("=" * 60)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | main() orchestration | FileNotFoundError guard, assert M1>=M0, step sequence, json.dump pattern |

---

## Summary

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-3: fit_models | 2 | 2 |
| A-4: run_lrt | 2 | 2 |
| A-12: main() | 1 | 1 |
| **Total** | **5** | **5** |
