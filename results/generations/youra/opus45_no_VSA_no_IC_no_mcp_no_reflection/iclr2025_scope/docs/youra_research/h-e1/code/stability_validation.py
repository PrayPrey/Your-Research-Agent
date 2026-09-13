"""Stability validation for SSM outputs."""

from typing import Dict, Any, Tuple
import torch
from torch import Tensor


def validate_ssm_stability(
    ssm_output: Tensor,
    transformer_output: Tensor
) -> Tuple[bool, float]:
    """
    Validate SSM output stability.

    Returns:
        is_stable: True if no NaN/Inf
        magnitude_ratio: SSM norm / Transformer norm
    """
    has_nan = torch.isnan(ssm_output).any().item()
    has_inf = torch.isinf(ssm_output).any().item()
    is_stable = not (has_nan or has_inf)

    ssm_norm = ssm_output.norm().item()
    tf_norm = transformer_output.norm().item()
    magnitude_ratio = ssm_norm / (tf_norm + 1e-6)

    return is_stable, magnitude_ratio


def compute_stability_metrics(
    ssm_outputs: Tensor,
    transformer_outputs: Tensor
) -> Dict[str, Any]:
    """Compute comprehensive stability metrics."""
    nan_count = torch.isnan(ssm_outputs).sum().item()
    inf_count = torch.isinf(ssm_outputs).sum().item()

    ssm_norm = ssm_outputs.norm().item()
    tf_norm = transformer_outputs.norm().item()
    magnitude_ratio = ssm_norm / (tf_norm + 1e-6)

    return {
        "nan_count": int(nan_count),
        "inf_count": int(inf_count),
        "magnitude_ratio": magnitude_ratio,
        "is_stable": nan_count == 0 and inf_count == 0,
        "max_value": ssm_outputs.max().item(),
        "min_value": ssm_outputs.min().item()
    }
