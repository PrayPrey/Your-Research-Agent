"""Random SSM initialization baseline."""

from typing import Tuple
import torch
from torch import Tensor


def random_init_ssm(
    d_model: int = 768,
    d_state: int = 64,
    seed: int = 42
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """
    Random SSM baseline, shape-matched to duality_init_ssm_from_attention.

    Returns:
        A: [d_model, d_state] ~ N(0,1)/sqrt(d_state)
        B: [d_state, d_model] Xavier uniform
        C: [d_model, d_state] Xavier uniform
        D: [d_model] zeros
        dt: [d_model] ones * 0.1
    """
    torch.manual_seed(seed)

    A = torch.randn(d_model, d_state) / (d_state ** 0.5)
    A = -torch.abs(A)  # negative for stability

    B = torch.empty(d_state, d_model)
    torch.nn.init.xavier_uniform_(B)

    C = torch.empty(d_model, d_state)
    torch.nn.init.xavier_uniform_(C)

    D = torch.zeros(d_model)
    dt = torch.ones(d_model) * 0.1

    return A, B, C, D, dt
