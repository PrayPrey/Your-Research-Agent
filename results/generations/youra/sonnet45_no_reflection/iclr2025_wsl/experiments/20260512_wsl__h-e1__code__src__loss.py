"""Loss functions for training"""

import torch
import torch.nn.functional as F


def reconstruction_loss(original: torch.Tensor, reconstructed: torch.Tensor) -> torch.Tensor:
    """
    Compute MSE reconstruction loss.
    Args:
        original: [B, D] original weights
        reconstructed: [B, D] reconstructed weights
    Returns:
        scalar loss
    """
    return F.mse_loss(reconstructed, original)


def equivariance_loss(model, weights: torch.Tensor, arch_labels: torch.Tensor) -> torch.Tensor:
    """
    Compute equivariance loss by applying random permutations.
    Args:
        model: SlotEquivariantEncoder instance
        weights: [B, D] weight vectors
        arch_labels: [B] architecture labels
    Returns:
        scalar loss measuring divergence under permutation
    """
    # Original encoding
    z_original = model(weights, arch_labels)

    # Apply random permutation to weights
    B, D = weights.shape
    perm_indices = torch.randperm(D, device=weights.device)
    weights_permuted = weights[:, perm_indices]

    # Permuted encoding
    z_permuted = model(weights_permuted, arch_labels)

    # Equivariance loss: encodings should be similar under permutation
    return F.mse_loss(z_original, z_permuted)


def combined_loss(
    model,
    weights: torch.Tensor,
    arch_labels: torch.Tensor,
    lambda_equiv: float
) -> tuple:
    """
    Compute combined loss: L_recon + λ_equiv * L_equiv
    Args:
        model: SlotEquivariantEncoder instance
        weights: [B, D] weight vectors
        arch_labels: [B] architecture labels
        lambda_equiv: equivariance loss weight
    Returns:
        (total_loss, recon_loss, equiv_loss)
    """
    # Forward pass
    z = model(weights, arch_labels)
    weights_recon = model.reconstruct_weights(z)

    # Reconstruction loss
    recon_loss = reconstruction_loss(weights, weights_recon)

    # Equivariance loss (only if lambda_equiv > 0)
    if lambda_equiv > 0:
        equiv_loss = equivariance_loss(model, weights, arch_labels)
    else:
        equiv_loss = torch.tensor(0.0, device=weights.device)

    # Combined loss
    total_loss = recon_loss + lambda_equiv * equiv_loss

    return total_loss, recon_loss, equiv_loss
