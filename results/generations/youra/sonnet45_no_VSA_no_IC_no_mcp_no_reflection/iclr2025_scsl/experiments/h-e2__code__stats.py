"""
Statistical tests for h-e2: F-test and paired t-test.
"""

import numpy as np
from scipy import stats


def variance_ratio_test(var_spurious: list[float], var_core: list[float]) -> dict:
    """
    F-test for variance ratio (H0: V_s/V_c = 1).

    Returns: {'f_stat': float, 'p_value': float, 'ratio': float}
    """
    var_s = np.array(var_spurious)
    var_c = np.array(var_core)

    # Remove zeros to avoid division issues
    var_s = var_s[var_s > 0]
    var_c = var_c[var_c > 0]

    if len(var_s) == 0 or len(var_c) == 0:
        return {'f_stat': float('nan'), 'p_value': float('nan'), 'ratio': float('nan')}

    mean_var_s = np.mean(var_s)
    mean_var_c = np.mean(var_c)
    ratio = mean_var_s / mean_var_c if mean_var_c > 0 else float('inf')

    # F-test
    f_stat = np.var(var_s) / np.var(var_c) if np.var(var_c) > 0 else float('inf')
    dfn = len(var_s) - 1
    dfd = len(var_c) - 1
    p_value = stats.f.sf(f_stat, dfn, dfd) if dfn > 0 and dfd > 0 else float('nan')

    return {
        'f_stat': f_stat,
        'p_value': p_value,
        'ratio': ratio
    }


def forgetting_paired_test(forgetting_s: list[float], forgetting_c: list[float]) -> dict:
    """
    Paired t-test for forgetting rates (H0: F_s = F_c).

    Returns: {'t_stat': float, 'p_value': float, 'mean_diff': float}
    """
    if len(forgetting_s) != len(forgetting_c):
        return {'t_stat': float('nan'), 'p_value': float('nan'), 'mean_diff': float('nan')}

    fs = np.array(forgetting_s)
    fc = np.array(forgetting_c)

    if len(fs) < 2:
        return {'t_stat': float('nan'), 'p_value': float('nan'), 'mean_diff': float(np.mean(fs) - np.mean(fc))}

    t_stat, p_value = stats.ttest_rel(fs, fc)

    return {
        't_stat': t_stat,
        'p_value': p_value,
        'mean_diff': np.mean(fs) - np.mean(fc)
    }
