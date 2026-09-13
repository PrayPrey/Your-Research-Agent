import math
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from sklearn.linear_model import LinearRegression
from sklearn.inspection import permutation_importance


def compute_vif(df) -> dict:
    X = df[['win_rate_std', 'avg_length_std']].copy()
    X_const = sm.add_constant(X)
    vif_win = variance_inflation_factor(X_const.values, 1)
    vif_len = variance_inflation_factor(X_const.values, 2)
    if math.isinf(vif_win) or math.isinf(vif_len):
        any_high = True
    else:
        any_high = any(v >= 5.0 for v in [vif_win, vif_len])
    return {'win_rate': float(vif_win), 'avg_length': float(vif_len), 'any_high_vif': any_high}


def fit_baseline_ols(df) -> dict:
    X = sm.add_constant(df['avg_length_std'])
    y = df['length_controlled_winrate']
    model = sm.OLS(y, X).fit()
    return {
        'beta_avg_length': float(model.params['avg_length_std']),
        'r2': float(model.rsquared),
        'pvalue': float(model.pvalues['avg_length_std'])
    }


def fit_full_ols(df) -> dict:
    X = sm.add_constant(df[['win_rate_std', 'avg_length_std']])
    y = df['length_controlled_winrate']
    model = sm.OLS(y, X).fit()
    return {
        'beta_win': float(model.params['win_rate_std']),
        'beta_len': float(model.params['avg_length_std']),
        'p_win': float(model.pvalues['win_rate_std']),
        'p_len': float(model.pvalues['avg_length_std']),
        'r2': float(model.rsquared),
        'r2_adj': float(model.rsquared_adj),
        'residuals': np.array(model.resid),
        'fitted': np.array(model.fittedvalues),
        '_model': model
    }


def run_ols_diagnostics(ols_result: dict, df) -> dict:
    model = ols_result['_model']
    X_exog = model.model.exog
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(model.resid, X_exog)
    return {
        'bp_stat': float(bp_stat),
        'bp_pvalue': float(bp_pvalue),
        'heteroscedastic': bool(bp_pvalue < 0.05)
    }


def run_permutation_fallback(df) -> dict:
    X = df[['win_rate_std', 'avg_length_std']].values
    y = df['length_controlled_winrate'].values
    lr = LinearRegression().fit(X, y)
    perm = permutation_importance(lr, X, y, n_repeats=30, random_state=42)
    return {
        'imp_win': float(perm.importances_mean[0]),
        'imp_len': float(perm.importances_mean[1])
    }
