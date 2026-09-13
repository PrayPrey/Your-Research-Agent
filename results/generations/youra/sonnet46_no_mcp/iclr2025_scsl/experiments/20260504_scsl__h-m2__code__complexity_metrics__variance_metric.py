import numpy as np
from scipy import stats
from typing import Dict, Any


def compute_intraclass_variance(features: np.ndarray) -> float:
    if features.shape[0] < 2:
        return 0.0
    cov = np.cov(features.T)
    return float(np.trace(cov))


def compute_variance_metric(
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
) -> Dict[str, Any]:
    var_spurious = compute_intraclass_variance(spurious_feats)
    var_core = compute_intraclass_variance(core_feats)

    per_feature_var_spurious = np.var(spurious_feats, axis=0)
    per_feature_var_core = np.var(core_feats, axis=0)

    t_stat, p_value = stats.ttest_ind(
        per_feature_var_spurious,
        per_feature_var_core,
        equal_var=False,
    )

    return {
        "var_spurious": var_spurious,
        "var_core": var_core,
        "per_feature_var_spurious": per_feature_var_spurious,
        "per_feature_var_core": per_feature_var_core,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "direction_correct": var_spurious < var_core,
    }
