"""Model definitions for H-M4: TransformerWithLoRA (new) + MambaWithLoRA (from h-m2)"""

import math
import torch
import torch.nn as nn
from transformers import AutoTokenizer
from peft import LoraConfig, get_peft_model

from config import MODEL_CONFIG, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA

try:
    from mamba_ssm import Mamba
    MAMBA_AVAILABLE = True
except ImportError:
    MAMBA_AVAILABLE = False


class MambaConfig:
    model_type = "mamba"
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MambaBlockSimulated(nn.Module):
    """Simulated Mamba block for when mamba-ssm is unavailable."""

    def __init__(self, d_model, d_state, d_conv, expand):
        super().__init__()
        d_inner = d_model * expand
        self.in_proj = nn.Linear(d_model, d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(d_inner, d_inner, d_conv, padding=d_conv - 1, groups=d_inner)
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)
        self.A_log = nn.Parameter(torch.randn(d_inner, d_state))
        self.D = nn.Parameter(torch.ones(d_inner))

    def forward(self, x):
        B, L, D = x.shape
        xz = self.in_proj(x)
        x_part, z = xz.chunk(2, dim=-1)
        x_part = x_part.transpose(1, 2)
        x_part = self.conv1d(x_part)[:, :, :L]
        x_part = x_part.transpose(1, 2)
        x_part = x_part * torch.sigmoid(z)
        return self.out_proj(x_part)


class MambaWithLoRA(nn.Module):
    """Mamba model with LoRA-compatible projection layers."""

    def __init__(self, d_model=512, d_state=16, n_layers=4, d_conv=4, expand=2, vocab_size=50304):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.config = MambaConfig(
            d_model=d_model, d_state=d_state, n_layers=n_layers,
            d_conv=d_conv, expand=expand, vocab_size=vocab_size, model_type="mamba"
        )

        self.embedding = nn.Embedding(vocab_size, d_model)

        if MAMBA_AVAILABLE:
            self.layers = nn.ModuleList([
                Mamba(d_model=d_model, d_state=d_state, d_conv=d_conv, expand=expand)
                for _ in range(n_layers)
            ])
        else:
            self.layers = nn.ModuleList([
                MambaBlockSimulated(d_model, d_state, d_conv, expand)
                for _ in range(n_layers)
            ])

        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, attention_mask=None, labels=None):
        x = self.embedding(input_ids)

        for layer in self.layers:
            x = layer(x) + x

        x = self.final_norm(x)
        logits = self.lm_head(x)

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(shift_logits.view(-1, self.vocab_size), shift_labels.view(-1))

        return type("Output", (), {"loss": loss, "logits": logits})()


class TransformerBlock(nn.Module):
    """Single transformer block with causal self-attention + FFN."""

    def __init__(self, d_model, n_heads, d_ff=None, dropout=0.1):
        super().__init__()
        d_ff = d_ff or d_model * 4
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff, bias=False),
            nn.GELU(),
            nn.Linear(d_ff, d_model, bias=False),
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, attention_mask=None):
        B, L, D = x.shape
        residual = x
        x = self.norm1(x)

        q = self.q_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)

        attn_weights = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        causal_mask = torch.triu(torch.ones(L, L, device=x.device, dtype=torch.bool), diagonal=1)
        attn_weights = attn_weights.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float('-inf'))

        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0).unsqueeze(1).unsqueeze(2)
            attn_weights = attn_weights.masked_fill(key_padding_mask, float('-inf'))

        attn_weights = torch.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)

        attn_out = torch.matmul(attn_weights, v)
        attn_out = attn_out.transpose(1, 2).contiguous().view(B, L, D)
        attn_out = self.o_proj(attn_out)

        x = residual + self.dropout(attn_out)

        residual = x
        x = self.norm2(x)
        x = residual + self.dropout(self.ffn(x))

        return x


class TransformerWithLoRA(nn.Module):
    """Causal decoder-only Transformer with LoRA-compatible projections."""

    def __init__(self, d_model=512, n_heads=8, n_layers=4, vocab_size=50304, max_seq_len=512, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.config = type("Config", (), {"model_type": "transformer", "d_model": d_model})()

        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_seq_len, d_model)

        self.layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads, dropout=dropout)
            for _ in range(n_layers)
        ])

        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, attention_mask=None, labels=None):
        B, L = input_ids.shape
        positions = torch.arange(L, device=input_ids.device).unsqueeze(0).expand(B, L)

        x = self.embedding(input_ids) + self.pos_embedding(positions)

        for layer in self.layers:
            x = layer(x, attention_mask)

        x = self.final_norm(x)
        logits = self.lm_head(x)

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(shift_logits.view(-1, self.vocab_size), shift_labels.view(-1))

        return type("Output", (), {"loss": loss, "logits": logits})()


def load_baseline_model(vocab_size=50304, d_model=512, n_layers=4, n_heads=8):
    """Load TransformerWithLoRA (no LoRA applied yet)."""
    model = TransformerWithLoRA(d_model=d_model, n_heads=n_heads, n_layers=n_layers, vocab_size=vocab_size)
    return model


def load_proposed_model(vocab_size=50304, d_model=512, n_layers=4):
    """Load MambaWithLoRA (no LoRA applied yet)."""
    model = MambaWithLoRA(d_model=d_model, d_state=MODEL_CONFIG["d_state"], n_layers=n_layers, vocab_size=vocab_size)
    return model


def load_tokenizer():
    """Load tokenizer."""
    try:
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained("openai-gpt")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer
