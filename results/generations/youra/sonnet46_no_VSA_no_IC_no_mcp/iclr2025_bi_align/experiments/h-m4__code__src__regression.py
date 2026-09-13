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
    statsmodels_summary = str(model.summary())

    rng = np.random.default_rng(seed)
    idx = np.arange(len(kl_values))
    boot_slopes = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        b_slope, *_ = stats.linregress(kl_values[s], gap_values[s])
        boot_slopes.append(b_slope)
    boot_ci = np.percentile(boot_slopes, [2.5, 97.5])

    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "t_stat": float(t_stat),
        "ci_parametric": [float(ci_low), float(ci_high)],
        "ci_bootstrap": boot_ci.tolist(),
        "statsmodels_summary": statsmodels_summary,
        "n": int(len(kl_values)),
    }
