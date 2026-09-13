import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Literal, Optional

from .low_rank import LowRankProjection


class TaskConditionedMamba(nn.Module):
    """Mamba block with low-rank task conditioning on Δ, B, C matrices."""

    def __init__(
        self,
        d_model: int,
        d_state: int,
        task_emb_dim: int,
        rank: int = 32,
        d_conv: int = 4,
        expand: int = 2,
        variant: Literal["all_matrices", "delta_only"] = "all_matrices",
    ):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = d_model * expand
        self.variant = variant

        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, d_conv, padding=d_conv - 1, groups=self.d_inner)

        self.delta_proj = nn.Linear(self.d_inner, self.d_inner, bias=False)
        self.B_proj = nn.Linear(self.d_inner, d_state, bias=False)
        self.C_proj = nn.Linear(self.d_inner, d_state, bias=False)

        self.A_log = nn.Parameter(torch.randn(self.d_inner, d_state))
        self.D = nn.Parameter(torch.ones(self.d_inner))

        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)

        self.delta_task_mod = LowRankProjection(task_emb_dim, self.d_inner, rank)
        if variant == "all_matrices":
            self.B_task_mod = LowRankProjection(task_emb_dim, d_state, rank)
            self.C_task_mod = LowRankProjection(task_emb_dim, d_state, rank)
        else:
            self.B_task_mod = None
            self.C_task_mod = None

    def forward(self, x: Tensor, task_embedding: Tensor) -> Tensor:
        B, L, D = x.shape

        xz = self.in_proj(x)
        x_inner, z = xz.chunk(2, dim=-1)

        x_conv = x_inner.transpose(1, 2)
        x_conv = self.conv1d(x_conv)[:, :, :L]
        x_inner = F.silu(x_conv.transpose(1, 2))

        delta = self.delta_proj(x_inner)
        B_mat = self.B_proj(x_inner)
        C_mat = self.C_proj(x_inner)

        delta_mod = self.delta_task_mod(task_embedding)
        delta = delta + delta_mod.unsqueeze(1)

        if self.variant == "all_matrices":
            B_mod = self.B_task_mod(task_embedding)
            C_mod = self.C_task_mod(task_embedding)
            B_mat = B_mat + B_mod.unsqueeze(1)
            C_mat = C_mat + C_mod.unsqueeze(1)

        delta = F.softplus(delta)
        A = -torch.exp(self.A_log)
        y, h_final = self._ssm_scan_with_state(x_inner, delta, A, B_mat, C_mat)

        y = y + self.D.unsqueeze(0).unsqueeze(0) * x_inner
        y = y * F.silu(z)

        return self.out_proj(y)

    def get_state(self, x: Tensor, task_embedding: Tensor) -> Tensor:
        B, L, D = x.shape

        xz = self.in_proj(x)
        x_inner, z = xz.chunk(2, dim=-1)

        x_conv = x_inner.transpose(1, 2)
        x_conv = self.conv1d(x_conv)[:, :, :L]
        x_inner = F.silu(x_conv.transpose(1, 2))

        delta = self.delta_proj(x_inner)
        B_mat = self.B_proj(x_inner)
        C_mat = self.C_proj(x_inner)

        delta_mod = self.delta_task_mod(task_embedding)
        delta = delta + delta_mod.unsqueeze(1)

        if self.variant == "all_matrices":
            B_mod = self.B_task_mod(task_embedding)
            C_mod = self.C_task_mod(task_embedding)
            B_mat = B_mat + B_mod.unsqueeze(1)
            C_mat = C_mat + C_mod.unsqueeze(1)

        delta = F.softplus(delta)
        A = -torch.exp(self.A_log)
        _, h_final = self._ssm_scan_with_state(x_inner, delta, A, B_mat, C_mat)

        return h_final

    def _ssm_scan_with_state(self, x: Tensor, delta: Tensor, A: Tensor, B: Tensor, C: Tensor):
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

        return torch.stack(ys, dim=1), h
