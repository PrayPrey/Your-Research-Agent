import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class VanillaMambaWrapper(nn.Module):
    """Simplified Mamba-like SSM for baseline overhead comparison.

    Does not use mamba_ssm package - implements core SSM logic directly
    for fair comparison without package dependencies.
    """

    def __init__(self, d_model: int, d_state: int, d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = d_model * expand

        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, d_conv, padding=d_conv - 1, groups=self.d_inner)

        self.delta_proj = nn.Linear(self.d_inner, self.d_inner, bias=False)
        self.B_proj = nn.Linear(self.d_inner, d_state, bias=False)
        self.C_proj = nn.Linear(self.d_inner, d_state, bias=False)

        self.A_log = nn.Parameter(torch.randn(self.d_inner, d_state))
        self.D = nn.Parameter(torch.ones(self.d_inner))

        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)

    def forward(self, x: Tensor) -> Tensor:
        B, L, D = x.shape

        xz = self.in_proj(x)
        x_inner, z = xz.chunk(2, dim=-1)

        x_conv = x_inner.transpose(1, 2)
        x_conv = self.conv1d(x_conv)[:, :, :L]
        x_inner = F.silu(x_conv.transpose(1, 2))

        delta = F.softplus(self.delta_proj(x_inner))
        B_mat = self.B_proj(x_inner)
        C_mat = self.C_proj(x_inner)

        A = -torch.exp(self.A_log)
        y = self._ssm_scan(x_inner, delta, A, B_mat, C_mat)

        y = y + self.D.unsqueeze(0).unsqueeze(0) * x_inner
        y = y * F.silu(z)

        return self.out_proj(y)

    def _ssm_scan(self, x: Tensor, delta: Tensor, A: Tensor, B: Tensor, C: Tensor) -> Tensor:
        B_batch, L, d_inner = x.shape
        d_state = B.shape[-1]

        h = torch.zeros(B_batch, d_inner, d_state, device=x.device, dtype=x.dtype)
        ys = []

        for t in range(L):
            delta_t = delta[:, t, :]
            B_t = B[:, t, :]
            C_t = C[:, t, :]
            x_t = x[:, t, :]

            dA = torch.exp(delta_t.unsqueeze(-1) * A.unsqueeze(0))
            dB = delta_t.unsqueeze(-1) * B_t.unsqueeze(1)

            h = dA * h + dB * x_t.unsqueeze(-1)
            y_t = (h * C_t.unsqueeze(1)).sum(dim=-1)
            ys.append(y_t)

        return torch.stack(ys, dim=1)
