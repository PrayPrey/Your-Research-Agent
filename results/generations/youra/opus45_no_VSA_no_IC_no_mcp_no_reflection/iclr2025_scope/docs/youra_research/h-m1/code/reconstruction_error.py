"""Reconstruction error metrics and statistical analysis."""

from typing import List, Dict
import torch
from torch import Tensor
from scipy import stats
import numpy as np


def compute_reconstruction_error(ssm_output: Tensor, attn_output: Tensor) -> float:
    """
    Frobenius norm between SSM and attention outputs.

    Args:
        ssm_output: [batch, seq_len, d_model]
        attn_output: [batch, seq_len, d_model]
    Returns:
        Scalar mean Frobenius norm
    """
    diff = ssm_output - attn_output
    return torch.linalg.matrix_norm(diff.float(), ord="fro").mean().item()


def paired_stats(duality_errors: List[float], random_errors: List[float]) -> Dict[str, float]:
    """
    Paired t-test and effect size (Cohen's d).

    Args:
        duality_errors: list of reconstruction errors for duality init
        random_errors: list of reconstruction errors for random init
    Returns:
        {mean_duality, mean_random, reduction_pct, p_value, cohens_d}
    """
    d = np.array(duality_errors)
    r = np.array(random_errors)

    mean_d = float(np.mean(d))
    mean_r = float(np.mean(r))

    reduction_pct = (mean_r - mean_d) / mean_r * 100 if mean_r > 0 else 0.0

    # Paired t-test (random vs duality)
    t_stat, p_value = stats.ttest_rel(r, d)

    # Cohen's d
    diff = r - d
    cohens_d = float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 0 else 0.0

    return {
        "mean_duality": mean_d,
        "mean_random": mean_r,
        "reduction_pct": reduction_pct,
        "p_value": float(p_value),
        "cohens_d": cohens_d
    }
