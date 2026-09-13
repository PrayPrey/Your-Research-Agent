"""
02_fit_models.py — H-M2 Model Fitting Suite
CT LR overdispersion test, baseline NB-2, proposed NB-2 (with/without decade FE).
Serializes all results to model_results.json.
"""

import json
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from pathlib import Path
from typing import Any

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


def ct_lr_test(df_tagged: pd.DataFrame) -> dict[str, Any]:
    """Cameron-Trivedi LR overdispersion test on tagged subset using FORMULA_BASELINE."""
    print("  Running Cameron-Trivedi LR overdispersion test...")
    try:
        poisson_res = smf.poisson(FORMULA_BASELINE, data=df_tagged).fit(method='bfgs', disp=False, maxiter=200)
        nb2_res = smf.negativebinomial(FORMULA_BASELINE, data=df_tagged, loglike_method='nb2').fit(
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
    """Fit NB-2 model and extract full results dict. Verbatim from H-E1."""
    print(f"  Fitting NB-2 [{label}]...")
    try:
        model = smf.negativebinomial(formula, data=df, loglike_method='nb2')
        result = model.fit(method=NB2_METHOD, maxiter=NB2_MAXITER, disp=NB2_DISP)
        converged = bool(result.mle_retvals.get('converged', True))

        if not converged:
            print(f"  BFGS did not converge for [{label}], trying Nelder-Mead fallback...")
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
        print(f"  [{label}] converged={converged}, llf={result.llf:.2f}, aic={result.aic:.2f}")
        return out

    except Exception as e:
        print(f"  ERROR fitting [{label}]: {e}")
        raise RuntimeError(f"NB-2 fit failed for [{label}]: {e}") from e


def extract_iv_stats(fit_result: dict[str, Any], iv_name: str) -> dict[str, float]:
    """Extract IRR, CI, p-value for any named IV from fit_nb2() output dict."""
    coef     = fit_result['params'][iv_name]
    ci       = fit_result['conf_int'][iv_name]   # [lower_log, upper_log]
    pval     = fit_result['pvalues'][iv_name]
    return {
        'irr':      float(np.exp(coef)),
        'ci_lower': float(np.exp(ci[0])),
        'ci_upper': float(np.exp(ci[1])),
        'pval':     float(pval),
    }


def compute_attenuation(irr_no_fe: float, irr_with_fe: float) -> float:
    """Attenuation ratio = IRR(no decade FE) / IRR(with decade FE)."""
    return irr_no_fe / irr_with_fe


def main():
    print("=" * 60)
    print("H-M2 Step 02: Model Fitting Suite")
    print("=" * 60)

    print(f"\n[1] Loading {TAGGED_PARQUET}...")
    df_tagged = pd.read_parquet(TAGGED_PARQUET)
    print(f"  Loaded N={len(df_tagged)} rows")

    df_tagged['N_tasks'] = df_tagged['N_tasks'].astype(int)
    for col in ['log_n_instances', 'log_n_features', 'age_years', 'age_sq', 'log_tag_count_p1']:
        if df_tagged[col].isna().any():
            df_tagged[col] = df_tagged[col].fillna(df_tagged[col].median())

    all_results = {}

    print("\n[2] Cameron-Trivedi LR overdispersion test...")
    all_results['ct_lr_test'] = ct_lr_test(df_tagged)

    print("\n[3] Fitting baseline NB-2 (controls-only on tagged subset)...")
    all_results['baseline'] = fit_nb2(FORMULA_BASELINE, df_tagged, "baseline")

    print("\n[4] Fitting proposed NB-2 (log_tag_count_p1 + controls + C(decade))...")
    proposed_with_fe = fit_nb2(FORMULA_PROPOSED, df_tagged, "proposed_with_fe")
    iv_stats_with_fe = extract_iv_stats(proposed_with_fe, "log_tag_count_p1")
    proposed_with_fe['log_tag_count_p1_stats'] = iv_stats_with_fe
    all_results['proposed_with_fe'] = proposed_with_fe

    print(f"\n  *** PRIMARY RESULT ***")
    print(f"  log_tag_count_p1 IRR = {iv_stats_with_fe['irr']:.4f}")
    print(f"  95% CI               = [{iv_stats_with_fe['ci_lower']:.4f}, {iv_stats_with_fe['ci_upper']:.4f}]")
    print(f"  p-value              = {iv_stats_with_fe['pval']:.4e}")

    print("\n[5] Fitting proposed NB-2 (no C(decade)) for attenuation...")
    proposed_no_fe = fit_nb2(FORMULA_NO_FE, df_tagged, "proposed_no_fe")
    iv_stats_no_fe = extract_iv_stats(proposed_no_fe, "log_tag_count_p1")
    proposed_no_fe['log_tag_count_p1_stats'] = iv_stats_no_fe
    all_results['proposed_no_fe'] = proposed_no_fe

    print("\n[6] Computing attenuation ratio...")
    attenuation = compute_attenuation(iv_stats_no_fe['irr'], iv_stats_with_fe['irr'])
    all_results['attenuation_ratio'] = float(attenuation)
    print(f"  IRR with FE={iv_stats_with_fe['irr']:.4f}, without FE={iv_stats_no_fe['irr']:.4f}")
    print(f"  Attenuation ratio = {attenuation:.4f}")

    print(f"\n[7] Serializing results to {MODEL_RESULTS}...")
    MODEL_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_RESULTS, 'w') as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"  Results saved to {MODEL_RESULTS}")

    print("\n Model fitting complete")


if __name__ == "__main__":
    main()
