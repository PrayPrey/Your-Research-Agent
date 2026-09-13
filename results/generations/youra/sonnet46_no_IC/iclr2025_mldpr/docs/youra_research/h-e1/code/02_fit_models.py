"""
02_fit_models.py — H-E1 Model Fitting Suite

Cameron-Trivedi LR overdispersion test, NB-2 baseline + proposed, RC-4/5/7 robustness checks.
Serializes all results to model_results.json.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from pathlib import Path
from typing import Any

# === PATHS ===
BASE_DIR        = "docs/youra_research/h-e1"
PREPROCESSED    = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS   = f"{BASE_DIR}/results/model_results.json"

# === FORMULAS ===
_CONTROLS        = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {_CONTROLS}"
FORMULA_PROPOSED = f"N_tasks ~ has_tags + {_CONTROLS}"
FORMULA_AGE_ONLY = "N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq"

# === NB-2 OPTIMIZER ===
NB2_METHOD  = "bfgs"
NB2_MAXITER = 100
NB2_DISP    = False

# === GATE THRESHOLDS ===
GATE_IRR_MIN      = 1.1
GATE_CI_LOWER_MIN = 1.1
GATE_PVAL_MAX     = 0.05
PARTIAL_CI_MIN    = 1.05

# === RC PARAMETERS ===
RC4_WINSORIZE_PCT = 99


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bool):
            return bool(obj)
        return super().default(obj)


def ct_lr_test(df: pd.DataFrame) -> dict[str, Any]:
    """Cameron-Trivedi LR overdispersion test: Poisson vs NB-2."""
    print("  Running Cameron-Trivedi LR overdispersion test...")
    try:
        poisson_res = smf.poisson(FORMULA_PROPOSED, data=df).fit(method='bfgs', disp=False, maxiter=200)
        nb2_res = smf.negativebinomial(FORMULA_PROPOSED, data=df, loglike_method='nb2').fit(
            method=NB2_METHOD, maxiter=NB2_MAXITER, disp=NB2_DISP)
        lr_stat = 2 * (nb2_res.llf - poisson_res.llf)
        p_value = float(stats.chi2.sf(lr_stat, df=1))
        result = {
            'lr_stat': float(lr_stat),
            'p_value': p_value,
            'nb2_appropriate': bool(p_value < 0.05)
        }
        print(f"  CT LR={lr_stat:.2f}, p={p_value:.4e}, NB-2 appropriate: {result['nb2_appropriate']}")
    except Exception as e:
        print(f"  WARNING: CT LR test failed: {e}")
        result = {'lr_stat': None, 'p_value': None, 'nb2_appropriate': True, 'error': str(e)}
    return result


def fit_nb2(formula: str, df: pd.DataFrame, label: str, target_col: str = "N_tasks") -> dict[str, Any]:
    """Fit NB-2 model and extract full results dict."""
    print(f"  Fitting NB-2 [{label}]...")
    try:
        model = smf.negativebinomial(formula, data=df, loglike_method='nb2')
        result = model.fit(method=NB2_METHOD, maxiter=NB2_MAXITER, disp=NB2_DISP)
        converged = bool(result.mle_retvals.get('converged', True))

        if not converged:
            print(f"  ⚠ BFGS did not converge for [{label}], trying Nelder-Mead fallback...")
            result = model.fit(method='nm', maxiter=500, disp=NB2_DISP)
            converged = bool(result.mle_retvals.get('converged', True))

        conf_int_df = result.conf_int()
        conf_int = {str(name): [float(row[0]), float(row[1])]
                    for name, row in conf_int_df.iterrows()}

        out = {
            'label': label,
            'converged': converged,
            'llf': float(result.llf),
            'aic': float(result.aic),
            'bic': float(result.bic),
            'n_obs': int(result.nobs),
            'params': {str(k): float(v) for k, v in result.params.items()},
            'bse': {str(k): float(v) for k, v in result.bse.items()},
            'pvalues': {str(k): float(v) for k, v in result.pvalues.items()},
            'conf_int': conf_int,
        }
        print(f"  ✓ [{label}] converged={converged}, llf={result.llf:.2f}, aic={result.aic:.2f}")
        return out

    except Exception as e:
        print(f"  ERROR fitting [{label}]: {e}")
        raise RuntimeError(f"NB-2 fit failed for [{label}]: {e}") from e


def extract_has_tags_stats(fit_result: dict[str, Any]) -> dict[str, float]:
    """Extract IRR, CI bounds, and p-value for has_tags coefficient."""
    coef = fit_result['params']['has_tags']
    ci   = fit_result['conf_int']['has_tags']
    pval = fit_result['pvalues']['has_tags']
    return {
        'irr':      float(np.exp(coef)),
        'ci_lower': float(np.exp(ci[0])),
        'ci_upper': float(np.exp(ci[1])),
        'pval':     float(pval),
    }


def rc4_winsorized(df: pd.DataFrame, percentile: float = RC4_WINSORIZE_PCT) -> dict[str, Any]:
    """RC-4: Winsorize N_tasks at given percentile, refit proposed model."""
    print(f"  RC-4: Winsorizing N_tasks at {percentile}th pct...")
    threshold = float(np.percentile(df['N_tasks'], percentile))
    n_winsorized = int((df['N_tasks'] > threshold).sum())
    df_w = df.copy()
    df_w['N_tasks'] = df_w['N_tasks'].clip(upper=threshold)
    print(f"  Winsorize threshold={threshold:.1f}, n_winsorized={n_winsorized}")
    fit = fit_nb2(FORMULA_PROPOSED, df_w, "rc4_winsorized")
    s = extract_has_tags_stats(fit)
    return {**s, 'winsorize_threshold': threshold, 'n_winsorized': n_winsorized}


def rc5_tagged_only(df: pd.DataFrame) -> dict[str, Any]:
    """RC-5: Restrict to tag_count >= 1, refit proposed model."""
    print("  RC-5: Tagged-only subset...")
    df_tagged = df[df['tag_count'] >= 1].copy()
    n_subset = len(df_tagged)
    print(f"  n_subset={n_subset}")
    if n_subset < 10:
        print("  WARNING: too few tagged samples for RC-5")
        return {'irr': None, 'ci_lower': None, 'ci_upper': None, 'pval': None, 'n_subset': n_subset}
    # has_tags=1 for all in subset; still include in formula for coefficient stability check
    # If perfectly collinear (all has_tags=1), skip
    if df_tagged['has_tags'].nunique() < 2:
        print("  RC-5: has_tags is constant in tagged-only subset, skipping fit")
        return {'irr': None, 'ci_lower': None, 'ci_upper': None, 'pval': None,
                'n_subset': n_subset, 'note': 'has_tags constant in subset'}
    fit = fit_nb2(FORMULA_PROPOSED, df_tagged, "rc5_tagged_only")
    s = extract_has_tags_stats(fit)
    return {**s, 'n_subset': n_subset}


def rc7_age_vs_decade(df: pd.DataFrame) -> dict[str, Any]:
    """RC-7: Compare proposed model with vs without C(decade) FE."""
    print("  RC-7: Age vs Decade FE comparison...")
    proposed   = fit_nb2(FORMULA_PROPOSED, df, "rc7_with_decade")
    age_only   = fit_nb2(FORMULA_AGE_ONLY, df, "rc7_without_decade")
    s_with     = extract_has_tags_stats(proposed)
    s_without  = extract_has_tags_stats(age_only)
    attenuation = s_without['irr'] / s_with['irr'] if s_with['irr'] else None
    print(f"  IRR with decade={s_with['irr']:.4f}, without={s_without['irr']:.4f}, "
          f"attenuation_ratio={attenuation:.4f}" if attenuation else "")
    return {
        'irr_with_decade':          s_with['irr'],
        'irr_without_decade':       s_without['irr'],
        'ci_lower_with_decade':     s_with['ci_lower'],
        'ci_lower_without_decade':  s_without['ci_lower'],
        'attenuation_ratio':        float(attenuation) if attenuation else None,
    }


def serialize_results(results: dict[str, Any], out_path: str) -> None:
    """Serialize all model results to JSON."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"  ✓ Results saved to {out_path}")


def main():
    print("=" * 60)
    print("H-E1 Step 02: Model Fitting Suite")
    print("=" * 60)

    print(f"\n[1] Loading {PREPROCESSED}...")
    df = pd.read_parquet(PREPROCESSED)
    print(f"  Loaded N={len(df)} rows")

    # Ensure N_tasks is integer
    df['N_tasks'] = df['N_tasks'].astype(int)
    # Ensure has_tags is integer
    df['has_tags'] = df['has_tags'].astype(int)
    # Fill any remaining NaN in key columns
    for col in ['log_n_instances', 'log_n_features', 'age_years', 'age_sq']:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    all_results = {}

    print("\n[2] Cameron-Trivedi LR overdispersion test...")
    all_results['ct_lr_test'] = ct_lr_test(df)

    print("\n[3] Fitting baseline NB-2 (controls-only)...")
    all_results['baseline'] = fit_nb2(FORMULA_BASELINE, df, "baseline")

    print("\n[4] Fitting proposed NB-2 (has_tags + controls)...")
    proposed = fit_nb2(FORMULA_PROPOSED, df, "proposed")
    has_tags_stats = extract_has_tags_stats(proposed)
    proposed['has_tags'] = has_tags_stats
    all_results['proposed'] = proposed
    print(f"\n  *** PRIMARY RESULT ***")
    print(f"  has_tags IRR    = {has_tags_stats['irr']:.4f}")
    print(f"  95% CI          = [{has_tags_stats['ci_lower']:.4f}, {has_tags_stats['ci_upper']:.4f}]")
    print(f"  p-value         = {has_tags_stats['pval']:.4e}")

    print("\n[5] RC-4: Winsorized...")
    all_results['rc4_winsorized'] = rc4_winsorized(df)

    print("\n[6] RC-5: Tagged-only subset...")
    all_results['rc5_tagged_only'] = rc5_tagged_only(df)

    print("\n[7] RC-7: Age vs Decade FE...")
    all_results['rc7_age_vs_decade'] = rc7_age_vs_decade(df)

    print(f"\n[8] Serializing results to {MODEL_RESULTS}...")
    serialize_results(all_results, MODEL_RESULTS)

    print("\n✅ Model fitting complete")


if __name__ == "__main__":
    main()
