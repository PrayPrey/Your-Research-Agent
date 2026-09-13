"""
SSD fitter using mohawk's ref implementation (materialize_mixer).
Key design: batch all n_layers fits simultaneously with independent parameters.
"""
import math
import sys
import torch
import torch.nn as nn
from config import Config

MOHAWK_REPO = "/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scope/docs/youra_research/h-e1/repos/mohawk"
if MOHAWK_REPO not in sys.path:
    sys.path.insert(0, MOHAWK_REPO)

from components.cores.discrete_mamba2_ref import materialize_mixer


def _layer_batch_size(N: int) -> int:
    """Adaptive batch size to avoid OOM at large N."""
    if N <= 2048:
        return 32
    elif N <= 4096:
        return 16
    elif N <= 8192:
        return 8
    return 4


def fit_batch_layers(
    attn_matrices: torch.Tensor,  # [n_layers, N, N] any dtype
    d_model: int,
    d_state: int,
    n_opt_steps: int,
    lr: float,
    device: torch.device,
) -> list:
    """
    Fit n_layers independent SSD blocks simultaneously (batched).
    Returns list of frobenius errors per layer.
    """
    n_layers, N, _ = attn_matrices.shape
    batch_size = _layer_batch_size(N)
    all_errors = []

    for start in range(0, n_layers, batch_size):
        end = min(start + batch_size, n_layers)
        chunk = attn_matrices[start:end]
        chunk_errors = _fit_chunk(chunk, d_model, d_state, n_opt_steps, lr, device)
        all_errors.extend(chunk_errors)

    return all_errors


def _fit_chunk(
    attn_matrices: torch.Tensor,  # [B, N, N] any dtype
    d_model: int,
    d_state: int,
    n_opt_steps: int,
    lr: float,
    device: torch.device,
) -> list:
    """Fit B independent SSD blocks simultaneously."""
    B, N, _ = attn_matrices.shape
    targets = attn_matrices.float().to(device)
    out_dim = d_model + 2 * d_state + 1

    W = nn.Parameter(torch.randn(B, out_dim, d_model, device=device, dtype=torch.float32) * 0.01)
    D_v = nn.Parameter(torch.ones(B, 1, device=device, dtype=torch.float32))
    u = torch.zeros(B, N, d_model, device=device, dtype=torch.float32)
    diag_idx = torch.arange(N, device=device)

    optimizer = torch.optim.Adam([W, D_v], lr=lr, betas=(0.9, 0.999))

    for step in range(n_opt_steps):
        optimizer.zero_grad()
        xBCA = torch.bmm(u, W.transpose(-1, -2))  # [B, N, out_dim]
        Bm = xBCA[..., d_model:d_model + d_state].unsqueeze(2)
        Cm = xBCA[..., d_model + d_state:d_model + 2 * d_state].unsqueeze(2)
        A = xBCA[..., -1:]
        T = materialize_mixer(A, Bm, Cm, None)  # [B, 1, N, N]
        T_sq = T.squeeze(1).clone()
        T_sq[:, diag_idx, diag_idx] = T_sq[:, diag_idx, diag_idx] + D_v
        loss = torch.linalg.matrix_norm(T_sq - targets, ord="fro").mean()
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        xBCA = torch.bmm(u, W.transpose(-1, -2))
        Bm = xBCA[..., d_model:d_model + d_state].unsqueeze(2)
        Cm = xBCA[..., d_model + d_state:d_model + 2 * d_state].unsqueeze(2)
        A = xBCA[..., -1:]
        T = materialize_mixer(A, Bm, Cm, None)
        T_sq = T.squeeze(1).clone()
        T_sq[:, diag_idx, diag_idx] = T_sq[:, diag_idx, diag_idx] + D_v
        per_layer_errors = torch.linalg.matrix_norm(T_sq - targets, ord="fro")

    del W, D_v, u, targets, T, T_sq, xBCA
    torch.cuda.empty_cache()
    return per_layer_errors.cpu().tolist()


class SSDFitter:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def fit_batch_and_measure(
        self,
        attn_matrices: torch.Tensor,  # [n_layers, N, N] bfloat16
    ) -> list:
        """Fit all layers at once. Returns list of per-layer Frobenius errors."""
        return fit_batch_layers(
            attn_matrices,
            self.cfg.d_model,
            self.cfg.d_state,
            self.cfg.n_opt_steps,
            self.cfg.lr,
            self.device,
        )

    def fit_and_measure(
        self,
        attn_matrix: torch.Tensor,  # [N, N] bfloat16
        hidden_states: torch.Tensor = None,
        log_loss_curve: bool = False,
    ) -> tuple:
        """Single-layer fit. Returns (frobenius_error, loss_curve)."""
        errors = fit_batch_layers(
            attn_matrix.unsqueeze(0),
            self.cfg.d_model,
            self.cfg.d_state,
            self.cfg.n_opt_steps,
            self.cfg.lr,
            self.device,
        )
        return errors[0], []

    def toeplitz_error(self, attn_matrix: torch.Tensor) -> float:
        """Best Toeplitz approximation via diagonal averaging."""
        import numpy as np
        A = attn_matrix.float().numpy()
        N = A.shape[0]
        T = np.zeros_like(A)
        for d in range(-(N - 1), N):
            diag = np.diagonal(A, offset=d)
            rows = np.arange(max(0, -d), min(N, N - d))
            cols = rows + d
            T[rows, cols] = float(diag.mean())
        return float(np.linalg.norm(A - T, ord="fro"))

    def toeplitz_errors_batch(self, attn_matrices: torch.Tensor) -> list:
        """Toeplitz error for each layer. attn_matrices: [n_layers, N, N]"""
        return [self.toeplitz_error(attn_matrices[i]) for i in range(len(attn_matrices))]


def verify_mechanism_activated(
    transfer_matrix: torch.Tensor,
    attn_matrix: torch.Tensor,
    seq_len: int,
    loss_curve: list,
) -> tuple:
    checks = {}
    checks["shape_correct"] = (
        transfer_matrix.shape == (seq_len, seq_len)
        and attn_matrix.shape == (seq_len, seq_len)
    )
    checks["matrix_differs_from_attention"] = not torch.allclose(
        transfer_matrix, attn_matrix, atol=1e-3
    )
    checks["loss_finite"] = (
        len(loss_curve) > 0
        and all(math.isfinite(v) for v in loss_curve)
    )
    if len(loss_curve) >= 2:
        initial, final = loss_curve[0], loss_curve[-1]
        checks["loss_decreased_10pct"] = (
            initial > 0 and (initial - final) / initial >= 0.10
        )
    else:
        checks["loss_decreased_10pct"] = False

    all_pass = all(checks.values())
    return all_pass, checks
