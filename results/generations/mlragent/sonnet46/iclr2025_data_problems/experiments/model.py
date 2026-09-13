"""Small GPT-style language model for DynaMix proxy experiments."""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from config import DEVICE


class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, dropout=0.1):
        super().__init__()
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.n_embd = n_embd
        self.head_size = n_embd // n_head

        self.c_attn = nn.Linear(n_embd, 3 * n_embd)
        self.c_proj = nn.Linear(n_embd, n_embd)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.size()
        qkv = self.c_attn(x)
        q, k, v = qkv.split(self.n_embd, dim=2)
        q = q.view(B, T, self.n_head, self.head_size).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_size).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_size).transpose(1, 2)

        # Causal self-attention with flash attention if available
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=0.0)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        y = self.resid_dropout(self.c_proj(y))
        return y


class MLP(nn.Module):
    def __init__(self, n_embd, dropout=0.1):
        super().__init__()
        self.c_fc = nn.Linear(n_embd, 4 * n_embd)
        self.gelu = nn.GELU()
        self.c_proj = nn.Linear(4 * n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.c_proj(self.gelu(self.c_fc(x))))


class Block(nn.Module):
    def __init__(self, n_embd, n_head, dropout=0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, dropout)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = MLP(n_embd, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class SmallGPT(nn.Module):
    """Small GPT-style language model for proxy experiments."""

    def __init__(self, vocab_size, n_embd, n_layer, n_head, seq_len, dropout=0.1):
        super().__init__()
        self.seq_len = seq_len
        self.n_embd = n_embd

        self.transformer = nn.ModuleDict({
            "wte": nn.Embedding(vocab_size, n_embd),
            "wpe": nn.Embedding(seq_len, n_embd),
            "drop": nn.Dropout(dropout),
            "h": nn.ModuleList([Block(n_embd, n_head, dropout) for _ in range(n_layer)]),
            "ln_f": nn.LayerNorm(n_embd),
        })
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

        # Weight tying
        self.transformer.wte.weight = self.lm_head.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)

    def num_parameters(self):
        return sum(p.numel() for p in self.parameters())

    def forward(self, idx, targets=None):
        B, T = idx.size()
        assert T <= self.seq_len, f"Sequence length {T} exceeds model maximum {self.seq_len}"

        pos = torch.arange(0, T, dtype=torch.long, device=idx.device)
        tok_emb = self.transformer.wte(idx)
        pos_emb = self.transformer.wpe(pos)
        x = self.transformer.drop(tok_emb + pos_emb)

        for block in self.transformer.h:
            x = block(x)
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))

        return logits, loss

    def compute_loss_on_domain(self, data_batch):
        """Compute loss on a given batch."""
        x = data_batch[:, :-1]
        y = data_batch[:, 1:]
        _, loss = self(x, y)
        return loss

    def compute_gradient_snr(self, data_batch):
        """Compute gradient SNR for the batch as a scalar."""
        losses = []
        for i in range(len(data_batch)):
            x = data_batch[i:i+1, :-1]
            y = data_batch[i:i+1, 1:]
            _, loss = self(x, y)
            losses.append(loss)

        losses_tensor = torch.stack(losses)
        mean_loss = losses_tensor.mean()
        var_loss = losses_tensor.var() + 1e-8

        # SNR approximation using loss variance as proxy for gradient variance
        snr = (mean_loss ** 2 / var_loss).item()
        return snr


def create_model(config_dict, vocab_size, seq_len, device=DEVICE):
    """Create a SmallGPT model from config dict."""
    model = SmallGPT(
        vocab_size=vocab_size,
        n_embd=config_dict["n_embd"],
        n_layer=config_dict["n_layer"],
        n_head=config_dict["n_head"],
        seq_len=seq_len,
    )
    return model.to(device)
