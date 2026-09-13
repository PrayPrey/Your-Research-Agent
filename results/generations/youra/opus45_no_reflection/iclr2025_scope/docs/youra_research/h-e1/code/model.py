"""H-E1 Models - Teacher (Phi-1.5), Student (Phi-Mamba), CAB Bridges"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
from typing import Optional, Dict, Any
from transformers import AutoModelForCausalLM, AutoConfig
from config import ExperimentConfig


@dataclass
class TeacherOutput:
    logits: torch.Tensor
    hidden_states: tuple
    attentions: tuple
    k_projs: list
    q_projs: list


class Teacher(nn.Module):
    def __init__(self, config: ExperimentConfig):
        super().__init__()
        self.config = config
        self.model = AutoModelForCausalLM.from_pretrained(
            config.teacher_name,
            attn_implementation="eager",
            output_attentions=True,
            output_hidden_states=True,
            torch_dtype=torch.bfloat16
        )
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad = False

    def forward(self, input_ids: torch.Tensor) -> TeacherOutput:
        with torch.no_grad():
            outputs = self.model(
                input_ids,
                output_attentions=True,
                output_hidden_states=True
            )
        k_projs = []
        q_projs = []
        for layer in self.model.model.layers:
            k_projs.append(layer.self_attn.k_proj.weight)
            q_projs.append(layer.self_attn.q_proj.weight)
        return TeacherOutput(
            logits=outputs.logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            k_projs=k_projs,
            q_projs=q_projs
        )


class Mamba2Mixer(nn.Module):
    def __init__(self, d_model: int, d_state: int = 64, n_heads: int = 32,
                 d_head: int = 64, chunk_size: int = 256):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.n_heads = n_heads
        self.d_head = d_head
        self.chunk_size = chunk_size

        self.in_proj = nn.Linear(d_model, 2 * d_model + 2 * n_heads * d_state + n_heads, bias=False)
        self.conv1d = nn.Conv1d(d_model, d_model, kernel_size=4, padding=3, groups=d_model)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

        self.A_log = nn.Parameter(torch.log(torch.linspace(1, 16, n_heads)))
        self.D = nn.Parameter(torch.ones(n_heads))

    def forward(self, x: torch.Tensor, return_mixer_matrix: bool = False,
                return_bc: bool = False) -> Dict[str, Any]:
        B, L, D = x.shape
        proj = self.in_proj(x)
        z = proj[:, :, :D]
        x_proj = proj[:, :, D:2*D]
        bc = proj[:, :, 2*D:2*D + 2*self.n_heads*self.d_state]
        dt = proj[:, :, -self.n_heads:]

        x_conv = self.conv1d(x_proj.transpose(1, 2))[:, :, :L].transpose(1, 2)
        x_conv = F.silu(x_conv)

        B_mat = bc[:, :, :self.n_heads*self.d_state].view(B, L, self.n_heads, self.d_state)
        C_mat = bc[:, :, self.n_heads*self.d_state:].view(B, L, self.n_heads, self.d_state)

        dt = F.softplus(dt)
        A = -torch.exp(self.A_log)

        y = self._ssm_scan(x_conv, A, B_mat, C_mat, dt, self.D)
        y = y * F.silu(z)
        out = self.out_proj(y)

        result = {"hidden_states": out}

        if return_mixer_matrix:
            result["transfer_matrix"] = self._compute_transfer_matrix(A, B_mat, C_mat, dt)

        if return_bc:
            result["B"] = B_mat
            result["C"] = C_mat

        return result

    def _ssm_scan(self, x: torch.Tensor, A: torch.Tensor, B: torch.Tensor,
                  C: torch.Tensor, dt: torch.Tensor, D: torch.Tensor) -> torch.Tensor:
        batch, seq_len, d_model = x.shape
        x_heads = x.view(batch, seq_len, self.n_heads, self.d_head)

        dA = torch.exp(dt.unsqueeze(-1) * A.view(1, 1, self.n_heads, 1))

        h = torch.zeros(batch, self.n_heads, self.d_state, self.d_head, device=x.device, dtype=x.dtype)
        outputs = []

        for t in range(seq_len):
            h = dA[:, t, :, :, None] * h + B[:, t, :, :, None] * x_heads[:, t, :, None, :]
            y_t = (C[:, t, :, :, None] * h).sum(dim=2)
            y_t = y_t + D.view(1, self.n_heads, 1) * x_heads[:, t]
            outputs.append(y_t)

        return torch.stack(outputs, dim=1).view(batch, seq_len, d_model)

    def _compute_transfer_matrix(self, A: torch.Tensor, B: torch.Tensor,
                                  C: torch.Tensor, dt: torch.Tensor) -> torch.Tensor:
        """Compute transfer matrix using efficient vectorized approach.
        For PoC, compute sampled positions to avoid O(L^2) memory."""
        batch, seq_len, n_heads, d_state = B.shape
        dA = torch.exp(dt.unsqueeze(-1) * A.view(1, 1, n_heads, 1))

        # Sample positions for PoC (every 8th position)
        sample_stride = max(1, seq_len // 64)
        sampled_len = (seq_len + sample_stride - 1) // sample_stride

        transfer = torch.zeros(batch, n_heads, sampled_len, sampled_len,
                               device=B.device, dtype=B.dtype)

        sampled_indices = list(range(0, seq_len, sample_stride))

        for ii, i in enumerate(sampled_indices):
            # Compute cumulative decay from position 0 to i
            cum_decay = torch.ones(batch, n_heads, d_state, device=B.device, dtype=B.dtype)
            decays = [cum_decay.clone()]
            for k in range(1, i + 1):
                cum_decay = cum_decay * dA[:, k]
                if k in sampled_indices:
                    decays.append(cum_decay.clone())

            for jj, j in enumerate(sampled_indices[:ii + 1]):
                # decay from j to i
                if j == 0:
                    decay = decays[ii] if ii < len(decays) else cum_decay
                else:
                    j_idx = sampled_indices.index(j) if j in sampled_indices else 0
                    decay = decays[ii] / (decays[j_idx] + 1e-8) if ii < len(decays) and j_idx < len(decays) else cum_decay

                contribution = (C[:, i] * decay * B[:, j]).sum(dim=-1)
                transfer[:, :, ii, jj] = contribution

        return transfer


class PhiMambaLayer(nn.Module):
    def __init__(self, hidden_size: int, num_heads: int, d_state: int):
        super().__init__()
        self.mixer = Mamba2Mixer(hidden_size, d_state, num_heads, hidden_size // num_heads)
        self.norm = nn.LayerNorm(hidden_size)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_size, 4 * hidden_size),
            nn.GELU(),
            nn.Linear(4 * hidden_size, hidden_size)
        )
        self.mlp_norm = nn.LayerNorm(hidden_size)

    def forward(self, hidden_states: torch.Tensor, return_mixer_matrix: bool = False,
                return_bc: bool = False) -> Dict[str, Any]:
        residual = hidden_states
        hidden_states = self.norm(hidden_states)
        mixer_out = self.mixer(hidden_states, return_mixer_matrix, return_bc)
        hidden_states = residual + mixer_out["hidden_states"]

        residual = hidden_states
        hidden_states = self.mlp_norm(hidden_states)
        hidden_states = residual + self.mlp(hidden_states)

        result = {"hidden_states": hidden_states}
        if "transfer_matrix" in mixer_out:
            result["transfer_matrix"] = mixer_out["transfer_matrix"]
        if "B" in mixer_out:
            result["B"] = mixer_out["B"]
            result["C"] = mixer_out["C"]

        return result


class PhiMambaStudent(nn.Module):
    def __init__(self, config: ExperimentConfig):
        super().__init__()
        self.config = config
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([
            PhiMambaLayer(config.hidden_size, config.num_heads, config.d_state)
            for _ in range(config.num_layers)
        ])
        self.norm = nn.LayerNorm(config.hidden_size)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

    def forward(self, input_ids: torch.Tensor, layer_idx: Optional[int] = None,
                return_mixer_matrix: bool = False, return_bc: bool = False) -> Dict[str, Any]:
        hidden_states = self.embed_tokens(input_ids)
        all_hidden_states = [hidden_states]
        layer_out = None

        for idx, layer in enumerate(self.layers):
            should_return = (layer_idx is None or idx == layer_idx)
            out = layer(
                hidden_states,
                return_mixer_matrix=return_mixer_matrix and should_return,
                return_bc=return_bc and should_return
            )
            hidden_states = out["hidden_states"]
            all_hidden_states.append(hidden_states)

            if idx == layer_idx:
                layer_out = out

        hidden_states = self.norm(hidden_states)
        logits = self.lm_head(hidden_states)

        result = {
            "logits": logits,
            "hidden_states": all_hidden_states
        }
        if layer_out is not None:
            result["layer_out"] = layer_out

        return result


class Bridge(nn.Module):
    def __init__(self, d_state: int, d_head: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_state, d_state * 2),
            nn.GELU(),
            nn.Linear(d_state * 2, d_head)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def init_student_from_teacher(student: PhiMambaStudent, teacher: Teacher):
    """Copy embedding and lm_head weights from teacher to student."""
    student.embed_tokens.weight.data.copy_(teacher.model.model.embed_tokens.weight.data)
    student.lm_head.weight.data.copy_(teacher.model.lm_head.weight.data)
