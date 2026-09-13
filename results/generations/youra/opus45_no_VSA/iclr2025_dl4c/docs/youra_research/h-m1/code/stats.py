"""Statistical analysis for H-M1 experiment."""
import numpy as np
from scipy import stats


def control_for_edit_length(
    mi_values: np.ndarray,
    edit_lengths: np.ndarray,
    condition_labels: np.ndarray,
    n_permutations: int = 10000,
) -> dict:
    """Control for edit length using residualized MI and permutation test."""
    # Fit linear regression: MI ~ edit_length
    if np.std(edit_lengths) < 1e-10:
        # All edit lengths identical — no control needed
        slope, intercept = 0.0, mi_values.mean()
    else:
        slope, intercept, _, _, _ = stats.linregress(edit_lengths, mi_values)

    # Compute residuals
    predicted = slope * edit_lengths + intercept
    residuals = mi_values - predicted

    # Split by condition
    rl_mask = condition_labels == "RL"
    ce_mask = condition_labels == "CE"

    residual_mi_rl = residuals[rl_mask].mean()
    residual_mi_ce = residuals[ce_mask].mean()

    # Observed difference
    observed_diff = residual_mi_rl - residual_mi_ce

    # Permutation test
    perm_diffs = []
    for _ in range(n_permutations):
        perm_labels = np.random.permutation(condition_labels)
        perm_rl_mask = perm_labels == "RL"
        perm_ce_mask = perm_labels == "CE"
        perm_diff = residuals[perm_rl_mask].mean() - residuals[perm_ce_mask].mean()
        perm_diffs.append(perm_diff)

    perm_diffs = np.array(perm_diffs)
    p_value = (np.abs(perm_diffs) >= np.abs(observed_diff)).mean()

    return {
        "mi_rl_raw": mi_values[rl_mask].mean(),
        "mi_ce_raw": mi_values[ce_mask].mean(),
        "mi_rl_controlled": residual_mi_rl,
        "mi_ce_controlled": residual_mi_ce,
        "observed_diff": observed_diff,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "perm_diffs": perm_diffs,
        "residuals": residuals,
        "slope": slope,
        "intercept": intercept,
    }


def compute_cohens_d(residuals: np.ndarray, condition_labels: np.ndarray) -> float:
    """Compute Cohen's d effect size on residuals."""
    rl_mask = condition_labels == "RL"
    ce_mask = condition_labels == "CE"

    rl_residuals = residuals[rl_mask]
    ce_residuals = residuals[ce_mask]

    mean_diff = rl_residuals.mean() - ce_residuals.mean()
    pooled_std = np.sqrt(
        (rl_residuals.var() * (len(rl_residuals) - 1) + ce_residuals.var() * (len(ce_residuals) - 1))
        / (len(rl_residuals) + len(ce_residuals) - 2)
    )

    return mean_diff / pooled_std if pooled_std > 0 else 0.0


def evaluate_hypothesis(results: dict) -> dict:
    """Gate check: I(F;E)_RL > I(F;E)_CE, p<0.05."""
    gate_passed = results["observed_diff"] > 0 and results["p_value"] < 0.05

    return {
        "gate_status": "PASS" if gate_passed else "FAIL",
        "mi_rl_controlled": results["mi_rl_controlled"],
        "mi_ce_controlled": results["mi_ce_controlled"],
        "difference": results["observed_diff"],
        "p_value": results["p_value"],
    }
