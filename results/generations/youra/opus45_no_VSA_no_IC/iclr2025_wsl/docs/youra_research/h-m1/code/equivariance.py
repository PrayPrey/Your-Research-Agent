"""Equivariance verification for NFN model."""
import torch
from typing import List, Tuple, Dict


def generate_neuron_permutation(weight_tensors: List[torch.Tensor], seed: int = 42) -> Dict[int, torch.Tensor]:
    """Generate random neuron permutation for each layer.

    For weight matrix W[out, in]:
    - Permuting output neurons = permuting rows of W and next layer's columns
    - Only permute hidden layer neurons (not input/output of the whole network)

    Returns dict mapping layer_idx -> permutation indices for output neurons.
    """
    torch.manual_seed(seed)
    perms = {}

    # Skip first and last layer (input/output dims are fixed)
    for i in range(len(weight_tensors) - 1):
        out_dim = weight_tensors[i].shape[1]  # shape is [B, out, in, ...]
        perms[i] = torch.randperm(out_dim)

    return perms


def apply_permutation(
    weight_tensors: List[torch.Tensor],
    permutation: Dict[int, torch.Tensor]
) -> List[torch.Tensor]:
    """Apply neuron permutation to weight tensors.

    When permuting layer i's output neurons:
    - Permute rows of W_i
    - Permute columns of W_{i+1}
    """
    permuted = [w.clone() for w in weight_tensors]

    for layer_idx, perm in permutation.items():
        # Permute rows of current layer's weights
        if layer_idx < len(permuted):
            w = permuted[layer_idx]
            permuted[layer_idx] = w[:, perm]  # Permute output dim

        # Permute columns of next layer's weights
        next_idx = layer_idx + 1
        if next_idx < len(permuted):
            w = permuted[next_idx]
            if w.dim() == 3:  # [B, out, in]
                permuted[next_idx] = w[:, :, perm]
            elif w.dim() == 5:  # [B, out, in, h, w]
                permuted[next_idx] = w[:, :, perm, :, :]

    return permuted


def verify_equivariance(
    model: torch.nn.Module,
    weight_tensors: List[torch.Tensor],
    permutation: Dict[int, torch.Tensor],
    atol: float = 1e-5,
    device: str = "cpu"
) -> Tuple[bool, float]:
    """Verify model output is invariant to neuron permutation.

    Returns:
        (passed, max_abs_diff)
    """
    model = model.to(device)
    model.eval()
    weight_tensors = [w.to(device) for w in weight_tensors]
    with torch.no_grad():
        # Original output
        original_out = model.get_invariant_repr(weight_tensors)

        # Permuted input
        permuted_weights = apply_permutation(weight_tensors, permutation)
        permuted_out = model.get_invariant_repr(permuted_weights)

        # Check invariance
        diff = (original_out - permuted_out).abs().max().item()
        passed = diff < atol

    return passed, diff


def equivariance_pass_rate(
    model: torch.nn.Module,
    test_items: list,
    n_trials: int = 10,
    atol: float = 1e-5,
    device: str = "cpu"
) -> Tuple[float, float]:
    """Test equivariance on multiple samples with different permutations.

    Returns:
        (pass_rate, max_error_seen)
    """
    from nfn_model import extract_weight_tensors

    passes = 0
    max_err = 0.0
    total = 0

    for idx, (sd, _) in enumerate(test_items[:100]):  # Test on subset
        weights = extract_weight_tensors(sd)
        for seed in range(n_trials):
            perm = generate_neuron_permutation(weights, seed=seed + idx * 1000)
            passed, err = verify_equivariance(model, weights, perm, atol=atol, device=device)
            if passed:
                passes += 1
            max_err = max(max_err, err)
            total += 1

    return passes / total if total > 0 else 0.0, max_err
