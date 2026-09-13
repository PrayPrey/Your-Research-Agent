"""H-C1: Sign-flip canonicalization for M=2 MLPs."""
import torch


def exact_majority_sign(weights: torch.Tensor) -> torch.Tensor:
    """
    Compute exact majority sign per row.
    weights: (d_out, d_in) → returns (d_out,) in {-1, 0, +1}
    0 means exact tie.
    """
    row_sign_sums = torch.sign(weights.float()).sum(dim=1)
    return torch.sign(row_sign_sums)


def canonicalize_sign_flip_m2(
    W1: torch.Tensor,  # (64, 784)
    W2: torch.Tensor,  # (10, 64)
) -> tuple:
    """
    Apply sign-flip canonicalization to M=2 MLP weight pair.
    Returns: (W1_canon, W2_canon, is_degenerate)
    is_degenerate=True if any neuron had exact sign tie.
    """
    majority = exact_majority_sign(W1)   # (64,)
    ties = (majority == 0)
    is_degenerate = bool(ties.any().item())
    majority = majority.clone()
    majority[ties] = 1                   # tie-breaking: default +1
    D = torch.diag(majority.float())     # (64, 64)
    W1_canon = D @ W1.float()           # (64, 784)
    W2_canon = W2.float() @ D           # (10, 64)
    return W1_canon, W2_canon, is_degenerate
