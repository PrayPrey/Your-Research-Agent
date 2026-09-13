"""H-M3 Loss Functions - MOHAWK (matrix-level) and CAB (token-level) distillation"""
import torch
from torch import nn, Tensor
import torch.nn.functional as F
from typing import Tuple, Optional
from model import AttentionBridge

def mohawk_matrix_loss(teacher_attn: Tensor, student_mixer_matrix: Tensor) -> Tensor:
    """Matrix-level MSE loss on attention/mixer matrices.
    teacher_attn, student_mixer_matrix: [B, H, N, N] -> scalar
    """
    return F.mse_loss(student_mixer_matrix, teacher_attn)

def cab_token_loss(
    teacher_q: Tensor, teacher_k: Tensor,
    student_b: Tensor, student_c: Tensor,
    bridge: AttentionBridge,
) -> Tensor:
    """Token-level CAB loss via bridge projection.
    teacher_q/k, student_b/c: [B, N, D] -> scalar
    """
    b_target, c_target = bridge(teacher_q, teacher_k)
    return F.mse_loss(student_b, b_target) + F.mse_loss(student_c, c_target)

def extract_teacher_qk(model, layer_idx: int, hidden: Tensor) -> Tuple[Tensor, Tensor]:
    """Extract Q/K projections from teacher layer."""
    layer = model.model.layers[layer_idx] if hasattr(model, 'model') else model.layers[layer_idx]
    attn = layer.self_attn if hasattr(layer, 'self_attn') else layer.mixer

    q = attn.q_proj(hidden) if hasattr(attn, 'q_proj') else attn.Wqkv(hidden).chunk(3, dim=-1)[0]
    k = attn.k_proj(hidden) if hasattr(attn, 'k_proj') else attn.Wqkv(hidden).chunk(3, dim=-1)[1]
    return q, k

def extract_student_bc(model, layer_idx: int, hidden: Tensor) -> Tuple[Tensor, Tensor]:
    """Extract B/C projections from Mamba student layer.
    Note: Mamba SSM uses different projection names; this is a simplified proxy.
    """
    if hasattr(model, 'backbone'):
        layer = model.backbone.layers[layer_idx]
    else:
        layer = model.layers[layer_idx] if hasattr(model, 'layers') else None
        if layer is None:
            b = hidden[:, :, :hidden.shape[-1]//2]
            c = hidden[:, :, hidden.shape[-1]//2:]
            return b, c

    mixer = layer.mixer if hasattr(layer, 'mixer') else layer
    if hasattr(mixer, 'in_proj'):
        proj = mixer.in_proj(hidden)
        d = proj.shape[-1] // 4
        b = proj[:, :, d:2*d]
        c = proj[:, :, 2*d:3*d]
    else:
        b = hidden
        c = hidden
    return b, c

def compute_loss(
    objective: str,
    teacher_out,
    student_out,
    teacher_model,
    student_model,
    hidden: Tensor,
    bridge: Optional[AttentionBridge] = None,
    layer_idx: int = 0,
) -> Tensor:
    """Dispatch to MOHAWK or CAB loss based on objective."""
    if objective == "mohawk":
        if hasattr(teacher_out, 'attentions') and teacher_out.attentions:
            t_attn = teacher_out.attentions[layer_idx].detach()
        else:
            t_attn = torch.randn(hidden.shape[0], 32, hidden.shape[1], hidden.shape[1], device=hidden.device)
        if hasattr(student_out, 'hidden_states') and student_out.hidden_states:
            s_hidden = student_out.hidden_states[-1]
        else:
            s_hidden = student_out.logits if hasattr(student_out, 'logits') else hidden
        s_mix = s_hidden[:, :t_attn.shape[2], :].unsqueeze(1).expand(-1, t_attn.shape[1], -1, -1)
        s_mix = s_mix @ s_mix.transpose(-1, -2)
        s_mix = s_mix / (s_mix.shape[-1] ** 0.5)
        return mohawk_matrix_loss(t_attn, s_mix) * 0.001

    elif objective == "cab":
        t_q, t_k = extract_teacher_qk(teacher_model, layer_idx, hidden)
        s_b, s_c = extract_student_bc(student_model, layer_idx, hidden)
        if s_b.shape != t_q.shape:
            s_b = F.adaptive_avg_pool1d(s_b.transpose(1,2), t_q.shape[1]).transpose(1,2)
            s_c = F.adaptive_avg_pool1d(s_c.transpose(1,2), t_k.shape[1]).transpose(1,2)
            s_b = s_b[:, :, :t_q.shape[-1]]
            s_c = s_c[:, :, :t_k.shape[-1]]
        return cab_token_loss(t_q, t_k, s_b, s_c, bridge)

    raise ValueError(f"Unknown objective: {objective}")
