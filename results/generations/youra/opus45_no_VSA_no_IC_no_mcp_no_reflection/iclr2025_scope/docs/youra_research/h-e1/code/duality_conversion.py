"""Duality-based SSM parameter initialization from Transformer attention."""

from typing import Tuple
import math
import torch
from torch import Tensor
from transformers.models.bert.modeling_bert import BertSelfAttention


def extract_attention_weights(
    attn_layer: BertSelfAttention
) -> Tuple[Tensor, Tensor, Tensor]:
    """Extract Q, K, V weight matrices from BERT attention layer."""
    W_q = attn_layer.query.weight.data.clone()  # [768, 768]
    W_k = attn_layer.key.weight.data.clone()
    W_v = attn_layer.value.weight.data.clone()
    return W_q, W_k, W_v


def duality_init_ssm_from_attention(
    attn_layer: BertSelfAttention,
    d_state: int = 64
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """
    Convert Transformer attention to SSM parameters via Mamba-2 duality.

    Returns:
        A: [d_model, d_state] state transition (negative for stability)
        B: [d_state, d_model] input-to-state
        C: [d_model, d_state] state-to-output
        D: [d_model] skip connection
        dt: [d_model] discretization step
    """
    W_q, W_k, W_v = extract_attention_weights(attn_layer)
    d_model = W_q.shape[0]  # 768

    # QK product scaled
    QK = W_q @ W_k.T / math.sqrt(d_model)  # [768, 768]

    # SVD for principal components
    U, S, Vh = torch.linalg.svd(QK, full_matrices=False)

    # A: diagonal negative for stability, from singular values
    A = -torch.abs(S[:d_state]).unsqueeze(0).expand(d_model, -1)  # [d_model, d_state]

    # B: input-to-state from key structure
    B = Vh[:d_state, :]  # [d_state, d_model]
    B = B / (B.norm() + 1e-6)

    # C: state-to-output from value structure
    C = U[:, :d_state]  # [d_model, d_state]
    C = C / (C.norm() + 1e-6)

    # D: skip connection
    D = torch.ones(d_model) * 0.1

    # dt: discretization step
    dt = torch.ones(d_model) * (1.0 / math.sqrt(d_model))

    return A, B, C, D, dt
