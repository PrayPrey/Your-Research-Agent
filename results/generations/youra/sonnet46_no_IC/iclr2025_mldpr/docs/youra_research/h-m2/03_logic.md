# Logic: H-M2 — Tag Count Dose-Response (NB-2 Mechanism PoC)

Applied: Standard statsmodels NB-2 pattern (Archon KB not relevant — diffusion model domain)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/02_fit_models.py`
**Relevant Symbols**:
- `fit_nb2(formula, df, label, target_col="N_tasks") -> dict[str, Any]` — returns full stats dict (not tuple)
- `ct_lr_test(df) -> dict[str, Any]` — uses module-level FORMULA_PROPOSED; needs adapting for h-m2
- `NumpyEncoder(json.JSONEncoder)` — handles np.integer, np.floating, np.ndarray, bool
- `extract_has_tags_stats(fit_result) -> dict` — extracts IRR from dict key, not result object

**Key Finding**: H-E1 `fit_nb2` returns `dict[str, Any]` (not `tuple[Any, dict]` as architecture spec shows). H-M2 must match this actual return type. Parameter names: `formula, df, label, target_col`.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-E1 Code)

```python
# From: docs/youra_research/h-e1/code/02_fit_models.py (ACTUAL CODE)

def fit_nb2(
    formula: str,
    df: pd.DataFrame,
    label: str,
    target_col: str = "N_tasks"   # ← actual default, not used in body but present
) -> dict[str, Any]:
    """Fit NB-2 model. Returns dict with keys: label, converged, llf, aic, bic,
    n_obs, params, bse, pvalues, conf_int."""
    # BFGS primary; Nelder-Mead fallback on non-convergence
    # conf_int stored as {param_name: [lower, upper]} (list, not DataFrame)
    # raises RuntimeError on exception

def ct_lr_test(df: pd.DataFrame) -> dict[str, Any]:
    """Cameron-Trivedi LR test. Uses module-level FORMULA_PROPOSED."""
    # Returns: {'lr_stat': float, 'p_value': float, 'nb2_appropriate': bool}
    # On failure: {'lr_stat': None, 'p_value': None, 'nb2_appropriate': True, 'error': str}

class NumpyEncoder(json.JSONEncoder):
    """Handles np.integer, np.floating, np.ndarray, bool for JSON serialization."""
    # Copy verbatim from H-E1
```

**Verified from**: `docs/youra_research/h-e1/code/02_fit_models.py` lines 44-75, 77-112

---

## A-4: fit_nb2 + extract_iv_stats + compute_attenuation [Complexity: 10, Budget: 3 subtasks]

### API Signatures

```python
# code/02_fit_models.py

from pathlib import Path
from typing import Any
import json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

PROJECT_ROOT   = Path(__file__).resolve().parents[4]
TAGGED_PARQUET = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"
MODEL_RESULTS  = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"

_CONTROLS        = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {_CONTROLS}"
FORMULA_PROPOSED = f"N_tasks ~ log_tag_count_p1 + {_CONTROLS}"
FORMULA_NO_FE    = "N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq"
NB2_METHOD  = "bfgs"
NB2_MAXITER = 100
NB2_DISP    = False

# === Copy verbatim from H-E1 ===
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj): ...  # identical to H-E1


def ct_lr_test(df_tagged: pd.DataFrame) -> dict[str, Any]:
    """Cameron-Trivedi LR test on tagged subset using FORMULA_BASELINE.
    Returns: {'lr_stat': float, 'p_value': float, 'nb2_appropriate': bool}"""
    # Note: H-E1 uses FORMULA_PROPOSED (has_tags + controls).
    # H-M2 uses FORMULA_BASELINE (controls-only) — overdispersion test doesn't need IV.
    ...


def fit_nb2(
    formula: str,
    df: pd.DataFrame,
    label: str,
    target_col: str = "N_tasks"
) -> dict[str, Any]:
    """Fit NB-2 model. Identical contract to H-E1 fit_nb2().
    Returns dict: {label, converged, llf, aic, bic, n_obs, params, bse, pvalues, conf_int}
    conf_int[param] = [lower, upper] as floats."""
    # Copy H-E1 implementation verbatim — same logic, same return shape.
    ...


def extract_iv_stats(fit_result: dict[str, Any], iv_name: str) -> dict[str, float]:
    """Extract IRR, CI, p-value for any named IV from fit_nb2() output dict.
    Returns: {'irr': float, 'ci_lower': float, 'ci_upper': float, 'pval': float}"""
    # fit_result['conf_int'][iv_name] = [lower_log, upper_log]
    coef     = fit_result['params'][iv_name]          # log scale
    ci       = fit_result['conf_int'][iv_name]        # [lower_log, upper_log]
    pval     = fit_result['pvalues'][iv_name]
    return {
        'irr':      float(np.exp(coef)),
        'ci_lower': float(np.exp(ci[0])),
        'ci_upper': float(np.exp(ci[1])),
        'pval':     float(pval),
    }


def compute_attenuation(irr_no_fe: float, irr_with_fe: float) -> float:
    """Attenuation ratio = IRR(no decade FE) / IRR(with decade FE).
    > 1.0 means decade FE attenuates tag-count coefficient."""
    return irr_no_fe / irr_with_fe


def main() -> None:
    # df_tagged shape: (≈2625, 8+) — N_tasks, log_tag_count_p1, log_n_instances,
    #                                  log_n_features, age_years, age_sq, decade, tag_count
    # [1] load tagged_subset.parquet
    # [2] ct_lr_test(df_tagged)
    # [3] fit_nb2(FORMULA_BASELINE, df_tagged, "baseline")
    # [4] fit_nb2(FORMULA_PROPOSED, df_tagged, "proposed_with_fe")
    # [5] fit_nb2(FORMULA_NO_FE, df_tagged, "proposed_no_fe")
    # [6] extract_iv_stats(proposed_with_fe, "log_tag_count_p1")
    # [7] extract_iv_stats(proposed_no_fe, "log_tag_count_p1")
    # [8] compute_attenuation(irr_no_fe, irr_with_fe)
    # [9] serialize all to MODEL_RESULTS (NumpyEncoder)
    ...
```

### Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df_tagged | (≈2625, 8+) | has_tags=1 subset from H-E1 parquet |
| fit_result['params'] | dict[str, float] | ~10-15 keys incl. log_tag_count_p1, decade dummies |
| fit_result['conf_int'] | dict[str, list[float, float]] | same keys as params |
| extract_iv_stats output | dict with 4 floats | irr, ci_lower, ci_upper, pval |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | fit_nb2 for h-m2 | Copy H-E1 fit_nb2 verbatim; adapt ct_lr_test to use FORMULA_BASELINE |
| L-4-2 | extract_iv_stats + compute_attenuation | New functions: extract by iv_name (not hardcoded 'has_tags'); attenuation ratio |
| L-4-3 | main() serialization | Wire 3 model fits → extract stats → attenuation → model_results.json |

---

## A-7: Integration Test [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
# code/05_integration_test.py  (or run as: python -m pytest code/test_integration.py)

from pathlib import Path
import subprocess, json, sys

PROJECT_ROOT = Path(__file__).resolve().parents[4]
H_M2_CODE    = PROJECT_ROOT / "docs/youra_research/h-m2/code"
H_M2_RESULTS = PROJECT_ROOT / "docs/youra_research/h-m2/results"
H_M2_FIGURES = PROJECT_ROOT / "docs/youra_research/h-m2/figures"

SCRIPTS = [
    "01_preprocess.py",
    "02_fit_models.py",
    "03_generate_figures.py",
    "04_evaluate_gate.py",
]

def run_script(script_name: str) -> subprocess.CompletedProcess:
    """Run a pipeline script; raise on non-zero exit."""
    ...

def verify_tagged_subset() -> None:
    """Assert tagged_subset.parquet exists and N in [500, 4000]."""
    import pandas as pd
    df = pd.read_parquet(H_M2_RESULTS / "tagged_subset.parquet")
    assert 500 <= len(df) <= 4000, f"Unexpected N={len(df)}"
    assert 'log_tag_count_p1' in df.columns
    assert (df['tag_count'] >= 1).all()

def verify_model_results() -> None:
    """Assert model_results.json has required keys and proposed model converged."""
    results = json.loads((H_M2_RESULTS / "model_results.json").read_text())
    assert 'proposed_with_fe' in results
    assert results['proposed_with_fe']['converged'] is True
    assert 'ct_lr_test' in results
    assert results['ct_lr_test']['lr_stat'] is not None

def verify_primary_results() -> None:
    """Assert primary_results.json has gate verdict and key metrics."""
    pr = json.loads((H_M2_RESULTS / "primary_results.json").read_text())
    assert pr['result'] in ('PASS', 'INFORMATIVE_NEGATIVE')
    assert 'IRR_P2' in pr and 'CI_lower_P2' in pr
    assert pr['n_tagged_subset'] > 500
    print(f"  Gate verdict: {pr['result']} (IRR={pr['IRR_P2']:.4f}, CI_lower={pr['CI_lower_P2']:.4f})")

def verify_figures() -> None:
    """Assert all 4 required figures exist and are non-empty."""
    for fname in ['fig1_gate_metrics.png', 'fig2_tag_count_distribution.png',
                  'fig3_partial_regression.png', 'fig4_attenuation_forest.png']:
        p = H_M2_FIGURES / fname
        assert p.exists() and p.stat().st_size > 1000, f"Missing or empty: {fname}"

def main() -> None:
    # [1] Run 4 scripts sequentially; fail fast on any non-zero exit
    # [2] verify_tagged_subset()
    # [3] verify_model_results()
    # [4] verify_primary_results()
    # [5] verify_figures()
    # [6] Print: "INTEGRATION TEST PASSED" or raise AssertionError
    ...

if __name__ == "__main__":
    main()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Integration test script | 4-script pipeline runner + 5 verification checks; single executable |

---

## Notes for Phase 4 Coder

1. `fit_nb2` in h-m2 is a **verbatim copy** of H-E1's implementation — same return shape `dict[str, Any]`.
2. `extract_iv_stats(fit_result, iv_name)` replaces H-E1's `extract_has_tags_stats(fit_result)` — parameterize the key name.
3. `ct_lr_test` in h-m2 uses `FORMULA_BASELINE` (controls-only), not `FORMULA_PROPOSED` — H-E1's version hardcodes `FORMULA_PROPOSED` with `has_tags`.
4. `conf_int` in the returned dict is already `{name: [lower, upper]}` as floats — no `.loc[]` needed.
5. Integration test goes in `code/05_integration_test.py`; run directly, no pytest framework needed.
