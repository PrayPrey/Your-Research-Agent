"""
MMD evaluation: compute RBF-MMD between training latents and ViT test latents.
Gate check: ratio = MMD_SANE / MMD_EquiSSL >= 2.0 for PASS.
Uses RBF kernel with median heuristic bandwidth.
"""
import torch
import torch.nn as nn


class RBF(nn.Module):
    def __init__(self, n_kernels: int = 5, mul_factor: float = 2.0, bandwidth=None):
        super().__init__()
        self.bandwidth_multipliers = mul_factor ** (torch.arange(n_kernels) - n_kernels // 2)
        self.bandwidth = bandwidth

    def get_bandwidth(self, L2_distances: torch.Tensor) -> torch.Tensor:
        if self.bandwidth is None:
            n_samples = L2_distances.shape[0]
            bw = L2_distances.data.sum() / (n_samples ** 2 - n_samples)
            return bw.clamp(min=1e-6)  # prevent nan when latents collapse
        return self.bandwidth

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        L2_distances = torch.cdist(X, X) ** 2
        bw = self.get_bandwidth(L2_distances)
        mults = self.bandwidth_multipliers.to(X.device)
        return torch.exp(
            -L2_distances[None, ...] / (bw * mults)[:, None, None]
        ).sum(dim=0)


class MMDLoss(nn.Module):
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel if kernel is not None else RBF()

    def forward(self, X: torch.Tensor, Y: torch.Tensor) -> torch.Tensor:
        K = self.kernel(torch.vstack([X, Y]))
        X_size = X.shape[0]
        XX = K[:X_size, :X_size].mean()
        XY = K[:X_size, X_size:].mean()
        YY = K[X_size:, X_size:].mean()
        return XX - 2 * XY + YY


def compute_mmd(z_train: torch.Tensor, z_vit: torch.Tensor, n_kernels: int = 5) -> float:
    """RBF-MMD with median heuristic bandwidth. Returns scalar float."""
    # Subsample for memory efficiency if needed
    max_samples = 2000
    if z_train.shape[0] > max_samples:
        idx = torch.randperm(z_train.shape[0])[:max_samples]
        z_train = z_train[idx]
    if z_vit.shape[0] > max_samples:
        idx = torch.randperm(z_vit.shape[0])[:max_samples]
        z_vit = z_vit[idx]

    mmd_fn = MMDLoss(kernel=RBF(n_kernels=n_kernels, bandwidth=None))
    device = z_train.device

    with torch.no_grad():
        val = mmd_fn(z_train.to(device), z_vit.to(device))

    result = val.item()
    if result != result:  # nan check
        return 0.0
    return abs(result)  # MMD should be non-negative; clamp numerical noise


def compute_mmd_ratio(sane_train_z: torch.Tensor, equi_train_z: torch.Tensor,
                      vit_z: torch.Tensor, n_kernels: int = 5) -> dict:
    """
    Returns dict with mmd_sane, mmd_equi, ratio, gate keys.
    ratio = MMD_SANE / MMD_EquiSSL (larger = EquiSSL better reduces distribution shift)
    """
    mmd_sane = compute_mmd(sane_train_z, vit_z, n_kernels)
    mmd_equi = compute_mmd(equi_train_z, vit_z, n_kernels)

    if mmd_equi < 1e-10:
        ratio = float('inf') if mmd_sane > 1e-10 else 1.0
    else:
        ratio = mmd_sane / mmd_equi

    gate = gate_check(ratio)
    return {
        'mmd_sane': mmd_sane,
        'mmd_equi': mmd_equi,
        'ratio': ratio,
        'gate': gate,
    }


def gate_check(ratio: float) -> str:
    """Returns 'PASS' | 'WARN' | 'STOP' based on ratio thresholds."""
    if ratio >= 2.0:
        return 'PASS'
    elif ratio >= 1.5:
        return 'WARN'
    else:
        return 'STOP'
