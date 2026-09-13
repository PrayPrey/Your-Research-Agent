"""Reference selective scan implementation."""

import torch
from torch import Tensor


def selective_scan_ref(
    x: Tensor,
    A: Tensor,
    B: Tensor,
    C: Tensor,
    D: Tensor,
    dt: Tensor
) -> Tensor:
    """
    Reference selective scan for SSM forward pass.

    Args:
        x: [batch, seq_len, d_model] input
        A: [d_model, d_state] state transition
        B: [d_state, d_model] input projection
        C: [d_model, d_state] output projection
        D: [d_model] skip connection
        dt: [d_model] discretization step

    Returns:
        y: [batch, seq_len, d_model] output
    """
    batch, seq_len, d_model = x.shape
    d_state = A.shape[1]
    device = x.device

    # Initialize hidden state
    h = torch.zeros(batch, d_model, d_state, device=device, dtype=x.dtype)

    # Discretize A and B
    A_bar = torch.exp(dt.unsqueeze(-1) * A)  # [d_model, d_state]
    B_bar = dt.unsqueeze(-1) * B.T  # [d_model, d_state]

    outputs = []
    for t in range(seq_len):
        x_t = x[:, t, :]  # [batch, d_model]

        # State update: h = A_bar * h + B_bar * x
        h = A_bar.unsqueeze(0) * h + B_bar.unsqueeze(0) * x_t.unsqueeze(-1)

        # Output: y = sum(C * h, dim=-1) + D * x
        y_t = (C.unsqueeze(0) * h).sum(dim=-1) + D.unsqueeze(0) * x_t
        outputs.append(y_t)

    return torch.stack(outputs, dim=1)
