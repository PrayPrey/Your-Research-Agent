"""H-M3: Fit NB-2 models — CT LR test, baseline, categorical primary, RC-6, RC-7."""
import json
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'results')

FORMULA_CONTROLS = 'log_n_instances + log_n_features + age_years + age_sq + C(decade)'
FORMULA_BASELINE = f'N_tasks ~ {FORMULA_CONTROLS}'
FORMULA_CAT = f'N_tasks ~ C(tag_count_cat) + {FORMULA_CONTROLS}'
FORMULA_RC6 = f'N_tasks ~ C(tag_count_cat)*C(decade) + log_n_instances + log_n_features + age_years + age_sq'
FORMULA_RC7 = f'N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq'
BONF_ALPHA = 0.0167


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def fit_nb2(formula, df, label, method='bfgs', maxiter=200):
    print(f"Fitting NB-2: {label}...")
    try:
        res = smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(
            method=method, maxiter=maxiter, disp=False)
        if not res.mle_retvals.get('converged', True) and method == 'bfgs':
            print(f"  BFGS not converged, trying nm...")
            res = smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(
                method='nm', maxiter=500, disp=False)
    except Exception as e:
        print(f"  {method} failed: {e}, trying nm...")
        res = smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(
            method='nm', maxiter=500, disp=False)

    conf = res.conf_int()
    result = {
        'label': label,
        'llf': float(res.llf),
        'aic': float(res.aic),
        'bic': float(res.bic),
        'nobs': int(res.nobs),
        'params': {k: float(v) for k, v in res.params.items()},
        'pvalues': {k: float(v) for k, v in res.pvalues.items()},
        'conf_int': {k: [float(conf.loc[k, 0]), float(conf.loc[k, 1])] for k in conf.index},
    }
    print(f"  LLF={res.llf:.2f}, AIC={res.aic:.2f}")
    return result, res


def ct_lr_test(df):
    print("Running CT LR overdispersion test...")
    poisson_res = smf.poisson(FORMULA_BASELINE, data=df).fit(method='bfgs', disp=False)
    nb2_res, _ = fit_nb2(FORMULA_BASELINE, df, 'NB2-baseline')
    lr_stat = 2 * (nb2_res['llf'] - float(poisson_res.llf))
    p_ct = 1 - chi2.cdf(lr_stat, df=1)
    print(f"CT LR={lr_stat:.2f}, p={p_ct:.2e}")
    return {
        'lr_stat': float(lr_stat),
        'p_value': float(p_ct),
        'appropriate': lr_stat > 3.84
    }, nb2_res


def extract_cat_irr(fit_result):
    irr = {}
    for k in fit_result['params']:
        if 'tag_count_cat' in k and '[T.' in k:
            label = k.replace('C(tag_count_cat)[T.', '').rstrip(']')
            irr[label] = {
                'irr': float(np.exp(fit_result['params'][k])),
                'ci_lower': float(np.exp(fit_result['conf_int'][k][0])),
                'ci_upper': float(np.exp(fit_result['conf_int'][k][1])),
                'pvalue': float(fit_result['pvalues'][k]),
                'log_coef': float(fit_result['params'][k]),
            }
    return irr


def check_monotonicity(cat_irr):
    try:
        v12 = cat_irr['1-2']['irr']
        v35 = cat_irr['3-5']['irr']
        v6p = cat_irr['6+']['irr']
    except KeyError as e:
        print(f"  Missing category key: {e}")
        return False, {}
    is_monotonic = v12 > 1.0 and v12 < v35 and v35 < v6p
    return is_monotonic, {'1-2': v12, '3-5': v35, '6+': v6p}


def test_adjacent_contrasts(fit_res_obj, bonf_alpha=BONF_ALPHA):
    pw = fit_res_obj.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
    pw_df = pw.result_frame
    print("Pairwise contrast index:")
    print(list(pw_df.index))

    adjacent_pairs = [('0', '1-2'), ('1-2', '3-5'), ('3-5', '6+')]
    adj_pvals = {}
    n_passing = 0

    for (a, b) in adjacent_pairs:
        key = f'{a}-{b}'
        matched_row = None
        for idx in pw_df.index:
            idx_str = str(idx)
            if (a in idx_str and b in idx_str):
                matched_row = idx
                break
        if matched_row is None:
            # try reverse
            for idx in pw_df.index:
                idx_str = str(idx)
                if (b in idx_str and a in idx_str):
                    matched_row = idx
                    break

        if matched_row is not None:
            row = pw_df.loc[matched_row]
            # get bonferroni p-value
            bonf_col = [c for c in pw_df.columns if 'bonferroni' in c.lower() and 'p' in c.lower()]
            if bonf_col:
                bonf_p = float(row[bonf_col[0]])
            else:
                raw_p_col = [c for c in pw_df.columns if c in ('P>|t|', 'P>|z|', 'pvalue')]
                raw_p = float(row[raw_p_col[0]]) if raw_p_col else float(row.iloc[3])
                bonf_p = min(1.0, raw_p * 3)
            adj_pvals[key] = bonf_p
            if bonf_p < bonf_alpha:
                n_passing += 1
            print(f"  Contrast {key}: bonf_p={bonf_p:.4e} {'PASS' if bonf_p < bonf_alpha else 'FAIL'}")
        else:
            print(f"  Contrast {key}: NOT FOUND in pairwise result")
            adj_pvals[key] = None

    return pw_df, n_passing, adj_pvals


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parquet_path = os.path.join(OUTPUT_DIR, 'preprocessed_m3.parquet')
    df = pd.read_parquet(parquet_path)
    print(f"Loaded: N={len(df)}")

    # CT LR test + baseline NB-2
    ct_result, nb2_baseline = ct_lr_test(df)

    # Primary categorical model
    cat_result, cat_res_obj = fit_nb2(FORMULA_CAT, df, 'NB2-categorical')

    # Extract IRRs
    cat_irr = extract_cat_irr(cat_result)
    print("Category IRRs:")
    for label, vals in sorted(cat_irr.items()):
        print(f"  IRR({label}): {vals['irr']:.4f} (CI=[{vals['ci_lower']:.4f},{vals['ci_upper']:.4f}]), p={vals['pvalue']:.3e}")

    # Monotonicity
    is_monotonic, irr_values = check_monotonicity(cat_irr)
    print(f"Monotonic ordering: {is_monotonic} — {irr_values}")

    # Adjacent contrasts
    pw_df, n_passing, adj_pvals = test_adjacent_contrasts(cat_res_obj)
    print(f"Adjacent contrasts passing: {n_passing}/3")

    # RC-6: decade interaction
    rc6_result, _ = fit_nb2(FORMULA_RC6, df, 'NB2-RC6-decade-interaction')

    # RC-7: no decade FE
    rc7_result, _ = fit_nb2(FORMULA_RC7, df, 'NB2-RC7-no-decade-FE')
    cat_irr_no_fe = extract_cat_irr(rc7_result)
    attenuation = {}
    for label in cat_irr:
        if label in cat_irr_no_fe:
            attenuation[label] = cat_irr_no_fe[label]['irr'] / cat_irr[label]['irr']
    print(f"Attenuation ratios (no FE / with FE): {attenuation}")

    model_results = {
        'ct_lr_test': ct_result,
        'nb2_baseline': nb2_baseline,
        'nb2_categorical': cat_result,
        'cat_irr': cat_irr,
        'is_monotonic': is_monotonic,
        'irr_values': irr_values,
        'n_adjacent_contrasts_passing': n_passing,
        'adj_pvals': adj_pvals,
        'rc6_aic': rc6_result['aic'],
        'rc7_result': rc7_result,
        'cat_irr_no_fe': cat_irr_no_fe,
        'attenuation_ratios': attenuation,
        'n_corpus': int(len(df)),
        'bonferroni_alpha': BONF_ALPHA,
    }

    out_path = os.path.join(OUTPUT_DIR, 'model_results.json')
    with open(out_path, 'w') as f:
        json.dump(model_results, f, indent=2, cls=NumpyEncoder)
    print(f"Model results saved: {out_path}")
    return model_results


if __name__ == '__main__':
    main()
