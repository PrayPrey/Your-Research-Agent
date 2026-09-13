# Logic Design: H-E1 — NB-2 Model Fitting Suite

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-05
**Focus:** Epic E2 — Model Fitting Suite (`02_fit_models.py`)

Applied: sequential-pipeline-with-serialized-results (fit all models → serialize JSON → downstream scripts read JSON)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code to analyze — `docs/youra_research/h-e1/code/` does not exist yet
**Serena Findings**: Green-field project. Existing artifact is corpus CSV only at `docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv`

**Archon KB Search Results:**
- Query: "statistical regression API design Python" → similarity 0.30–0.44, all diffusion model results (unrelated domain)
- Query: "NB-2 negative binomial statsmodels count regression" → similarity 0.28–0.41, all deep learning results (unrelated domain)
- **Conclusion:** Archon KB contains no econometrics/statistics content. Implementation grounded in statsmodels official documentation and Phase 2C experiment brief.

---

## API Signatures

### Module: `02_fit_models.py`

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
import json
from pathlib import Path
from typing import Any

# ── Constants ────────────────────────────────────────────────────────────────
IN_PATH = "docs/youra_research/h-e1/results/preprocessed.parquet"
OUT_PATH = "docs/youra_research/h-e1/results/model_results.json"

CONTROLS = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {CONTROLS}"
FORMULA_PROPOSED = f"N_tasks ~ has_tags + {CONTROLS}"
FORMULA_AGE_ONLY = f"N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq"

NB2_LOGLIKE_METHOD = "nb2"
NB2_OPTIMIZER = "bfgs"
NB2_MAXITER = 100


# ── Core Functions ────────────────────────────────────────────────────────────

def ct_lr_test(df: pd.DataFrame) -> dict[str, Any]:
    """
    Cameron-Trivedi LR overdispersion test: Poisson vs NB-2.

    Args:
        df: preprocessed DataFrame with all derived features

    Returns:
        {
            "lr_stat": float,       # 2*(llf_nb2 - llf_poisson)
            "p_value": float,       # chi2(1) p-value under H0: alpha=0
            "nb2_appropriate": bool # True if p < 0.05
        }

    Note: Expected LR >> 3.84 based on prior h-e1 (CT LR=2222.68)
    """


def fit_nb2(
    formula: str,
    df: pd.DataFrame,
    label: str,
    target_col: str = "N_tasks"
) -> dict[str, Any]:
    """
    Fit NB-2 model and extract full results.

    Args:
        formula: patsy formula string (e.g., FORMULA_PROPOSED)
        df: preprocessed DataFrame
        label: descriptive label for this model (e.g., "proposed", "baseline")
        target_col: dependent variable column name

    Returns:
        {
            "label": str,
            "converged": bool,
            "llf": float,
            "aic": float,
            "bic": float,
            "n_obs": int,
            "params": dict[str, float],     # {coef_name: value}
            "bse": dict[str, float],        # standard errors
            "pvalues": dict[str, float],
            "conf_int": dict[str, list]     # {coef_name: [lower, upper]}
        }

    Raises:
        RuntimeError if model fails to converge after maxiter=100
    """


def extract_has_tags_stats(fit_result: dict[str, Any]) -> dict[str, float]:
    """
    Extract IRR, CI bounds, and p-value for the has_tags coefficient.

    Args:
        fit_result: output dict from fit_nb2()

    Returns:
        {
            "irr": float,       # exp(beta_has_tags)
            "ci_lower": float,  # exp(conf_int[has_tags][0])
            "ci_upper": float,  # exp(conf_int[has_tags][1])
            "pval": float       # pvalues[has_tags]
        }

    Note: Uses 95% CI from result.conf_int() (Wald-based in statsmodels)
    """


def rc4_winsorized(
    df: pd.DataFrame,
    percentile: float = 99.0
) -> dict[str, Any]:
    """
    RC-4: Winsorize N_tasks at given percentile, refit proposed model.

    Args:
        df: preprocessed DataFrame
        percentile: winsorization upper percentile (default 99)

    Returns:
        {
            "irr": float,
            "ci_lower": float,
            "ci_upper": float,
            "pval": float,
            "winsorize_threshold": float,   # actual clip value
            "n_winsorized": int             # count of rows affected
        }
    """


def rc5_tagged_only(df: pd.DataFrame) -> dict[str, Any]:
    """
    RC-5: Restrict to tag_count >= 1 (all-tagged subset), refit proposed model.

    Args:
        df: preprocessed DataFrame

    Returns:
        {
            "irr": float,
            "ci_lower": float,
            "ci_upper": float,
            "pval": float,
            "n_subset": int     # size of tagged-only subset
        }

    Note: has_tags=1 for all rows in this subset by definition;
          this checks if tag_count (continuous) variation drives effect
    """


def rc7_age_vs_decade(df: pd.DataFrame) -> dict[str, Any]:
    """
    RC-7: Compare proposed model with C(decade) FE vs age_years+age_sq only.

    Args:
        df: preprocessed DataFrame

    Returns:
        {
            "irr_with_decade": float,       # from FORMULA_PROPOSED (main model)
            "irr_without_decade": float,    # from FORMULA_AGE_ONLY
            "ci_lower_with_decade": float,
            "ci_lower_without_decade": float,
            "attenuation_ratio": float      # irr_without / irr_with (>1 = decade absorbs)
        }

    Note: Quantifies RC-3 risk (decade FE absorbing has_tags effect)
    """


def serialize_results(results: dict[str, Any], out_path: str) -> None:
    """
    Serialize all model results to JSON.

    Args:
        results: complete results dict (see JSON Output Schema below)
        out_path: output file path

    Note: numpy float64 → Python float via custom encoder
    """


def main() -> None:
    """
    Main orchestration: load parquet → run all models → serialize JSON.

    Execution order:
    1. Load preprocessed.parquet
    2. ct_lr_test(df)
    3. fit_nb2(FORMULA_BASELINE, df, "baseline")
    4. fit_nb2(FORMULA_PROPOSED, df, "proposed") → extract_has_tags_stats()
    5. rc4_winsorized(df)
    6. rc5_tagged_only(df)
    7. rc7_age_vs_decade(df)
    8. serialize_results(all_results, OUT_PATH)
    """
```

---

## Pseudo-code

### `ct_lr_test(df)`
```
poisson_result = smf.poisson(FORMULA_PROPOSED, data=df).fit(method='bfgs', disp=False)
nb2_result = smf.negativebinomial(FORMULA_PROPOSED, data=df, loglike_method='nb2')
              .fit(method='bfgs', maxiter=100, disp=False)

lr_stat = 2 * (nb2_result.llf - poisson_result.llf)
p_value = scipy.stats.chi2.sf(lr_stat, df=1)   # one-sided, H0: alpha=0

return {lr_stat, p_value, nb2_appropriate: p_value < 0.05}
```

### `fit_nb2(formula, df, label)`
```
model = smf.negativebinomial(formula, data=df, loglike_method='nb2')
result = model.fit(method='bfgs', maxiter=100, disp=False)

if not result.mle_retvals['converged']:
    log warning; try method='nm' (Nelder-Mead) as fallback

conf_int_df = result.conf_int()   # DataFrame, index=coef names, cols=[0, 1]

return {
    label,
    converged: result.mle_retvals['converged'],
    llf: result.llf,
    aic: result.aic,
    bic: result.bic,
    n_obs: int(result.nobs),
    params: result.params.to_dict(),
    bse: result.bse.to_dict(),
    pvalues: result.pvalues.to_dict(),
    conf_int: {name: [row[0], row[1]] for name, row in conf_int_df.iterrows()}
}
```

### `extract_has_tags_stats(fit_result)`
```
coef = fit_result['params']['has_tags']
ci = fit_result['conf_int']['has_tags']   # [lower, upper] on log scale

return {
    irr:      np.exp(coef),
    ci_lower: np.exp(ci[0]),
    ci_upper: np.exp(ci[1]),
    pval:     fit_result['pvalues']['has_tags']
}
```

### `rc4_winsorized(df, percentile=99)`
```
threshold = np.percentile(df['N_tasks'], percentile)
df_w = df.copy()
df_w['N_tasks'] = df_w['N_tasks'].clip(upper=threshold)
n_winsorized = (df['N_tasks'] > threshold).sum()

result = fit_nb2(FORMULA_PROPOSED, df_w, "rc4_winsorized")
stats = extract_has_tags_stats(result)

return {**stats, winsorize_threshold: threshold, n_winsorized: int(n_winsorized)}
```

### `rc5_tagged_only(df)`
```
df_tagged = df[df['tag_count'] >= 1].copy()
n_subset = len(df_tagged)

# Note: has_tags=1 for all rows; effect of tag_count variation on N_tasks
# Use FORMULA_PROPOSED (has_tags still in formula; collinear but tests stability)
result = fit_nb2(FORMULA_PROPOSED, df_tagged, "rc5_tagged_only")
stats = extract_has_tags_stats(result)

return {**stats, n_subset: n_subset}
```

### `rc7_age_vs_decade(df)`
```
# Main model (already fitted as proposed): has decade FE
proposed = fit_nb2(FORMULA_PROPOSED, df, "rc7_with_decade")
stats_with = extract_has_tags_stats(proposed)

# Age-only model: no C(decade)
age_only = fit_nb2(FORMULA_AGE_ONLY, df, "rc7_without_decade")
stats_without = extract_has_tags_stats(age_only)

attenuation = stats_without['irr'] / stats_with['irr']  # >1 means decade absorbs

return {
    irr_with_decade:         stats_with['irr'],
    irr_without_decade:      stats_without['irr'],
    ci_lower_with_decade:    stats_with['ci_lower'],
    ci_lower_without_decade: stats_without['ci_lower'],
    attenuation_ratio:       attenuation
}
```

---

## JSON Output Schema (`model_results.json`)

```json
{
    "ct_lr_test": {
        "lr_stat": 2222.68,
        "p_value": 0.0,
        "nb2_appropriate": true
    },
    "baseline": {
        "label": "controls_only",
        "converged": true,
        "llf": -12345.6,
        "aic": 24710.0,
        "bic": 24780.0,
        "n_obs": 5217,
        "params": {"log_n_instances": 0.12, "log_n_features": 0.08, "...": "..."},
        "pvalues": {"log_n_instances": 0.001, "...": "..."},
        "conf_int": {"log_n_instances": [0.08, 0.16], "...": "..."}
    },
    "proposed": {
        "label": "has_tags_model",
        "converged": true,
        "llf": -12300.0,
        "aic": 24620.0,
        "bic": 24700.0,
        "n_obs": 5217,
        "params": {"has_tags": 0.12, "log_n_instances": 0.11, "...": "..."},
        "bse": {"has_tags": 0.03, "...": "..."},
        "pvalues": {"has_tags": 0.0001, "...": "..."},
        "conf_int": {"has_tags": [0.06, 0.18], "...": "..."},
        "has_tags": {
            "irr": 1.13,
            "ci_lower": 1.06,
            "ci_upper": 1.20,
            "pval": 0.0001
        }
    },
    "rc4_winsorized": {
        "irr": 1.11,
        "ci_lower": 1.05,
        "ci_upper": 1.18,
        "pval": 0.0005,
        "winsorize_threshold": 250.0,
        "n_winsorized": 52
    },
    "rc5_tagged_only": {
        "irr": 1.08,
        "ci_lower": 1.02,
        "ci_upper": 1.15,
        "pval": 0.012,
        "n_subset": 3100
    },
    "rc7_age_vs_decade": {
        "irr_with_decade": 1.13,
        "irr_without_decade": 1.15,
        "ci_lower_with_decade": 1.06,
        "ci_lower_without_decade": 1.08,
        "attenuation_ratio": 1.02
    }
}
```

---

## Subtasks

### Subtask L-E2-1: NB-2 Core Fitting Functions
**Parent Epic:** E2 (complexity=12)
**Description:** Implement `ct_lr_test`, `fit_nb2`, and `extract_has_tags_stats` in `02_fit_models.py`. These are the primary model fitting functions used by all downstream RC variants.
**Acceptance Criteria:**
- `ct_lr_test` returns dict with lr_stat, p_value, nb2_appropriate
- `fit_nb2` handles BFGS convergence failure with Nelder-Mead fallback
- `extract_has_tags_stats` correctly applies `np.exp()` to log-scale params and conf_int
- All three functions return serializable dicts (no statsmodels objects)

### Subtask L-E2-2: Robustness Check Functions
**Parent Epic:** E2 (complexity=12)
**Description:** Implement `rc4_winsorized`, `rc5_tagged_only`, `rc7_age_vs_decade`, and `main()` in `02_fit_models.py`. RC functions reuse `fit_nb2` and `extract_has_tags_stats`.
**Acceptance Criteria:**
- RC-4 correctly clips N_tasks at 99th percentile; reports n_winsorized
- RC-5 restricts to tag_count >= 1; reports n_subset
- RC-7 fits both with-decade and without-decade models; computes attenuation_ratio
- `main()` runs all 7 model fits in correct order; serializes complete JSON
- `model_results.json` is valid JSON with all expected keys
