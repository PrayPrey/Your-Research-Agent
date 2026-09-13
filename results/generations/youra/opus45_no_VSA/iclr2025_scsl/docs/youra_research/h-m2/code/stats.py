import numpy as np
from scipy import stats


def aggregate_across_seeds(results: list) -> dict:
    srs = [r["sr"] for r in results if r.get("sr") is not None]
    wgas = [r["wga"] for r in results]
    return {
        "sr_mean": np.mean(srs) if srs else None,
        "sr_std": np.std(srs) if srs else None,
        "wga_mean": np.mean(wgas),
        "wga_std": np.std(wgas),
    }


def sr_significance_test(baseline_srs: list, parity_srs: list) -> dict:
    if len(baseline_srs) < 2 or len(parity_srs) < 2:
        return {"t_stat": 0, "p_value": 1.0, "significant": False}
    t, p = stats.ttest_ind(baseline_srs, parity_srs, equal_var=False)
    return {"t_stat": float(t), "p_value": float(p), "significant": p < 0.05}
