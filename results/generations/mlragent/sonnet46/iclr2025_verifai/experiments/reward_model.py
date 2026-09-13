"""
Learned reward model for verifiability potential estimation.
Lightweight model trained on (partial program, verification outcome) pairs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Optional, Tuple


class VerifiabilityRewardModel(nn.Module):
    """
    Reward model R_psi that estimates verifiability potential.
    Takes partial program features + SMT/execution signals as input.
    Outputs estimated probability that program will pass all checks.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        embed_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embed_dim = embed_dim

        # Token embedding for code tokens (simplified)
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # Transformer encoder for code
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=4,
            dim_feedforward=hidden_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Feature fusion: code representation + smt_signal + exec_signal
        self.fusion = nn.Sequential(
            nn.Linear(embed_dim + 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),
        )

    def forward(
        self,
        token_ids: torch.Tensor,      # (B, L)
        smt_signal: torch.Tensor,     # (B,) in [0, 1]
        exec_signal: torch.Tensor,    # (B,) in [0, 1]
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Returns verifiability potential score in [0, 1]."""
        B, L = token_ids.shape

        # Embed and encode
        x = self.embedding(token_ids)  # (B, L, D)
        if attention_mask is not None:
            src_key_padding_mask = ~attention_mask.bool()
        else:
            src_key_padding_mask = None

        encoded = self.encoder(x, src_key_padding_mask=src_key_padding_mask)  # (B, L, D)

        # Pool over sequence
        if attention_mask is not None:
            mask_expanded = attention_mask.unsqueeze(-1).float()
            pooled = (encoded * mask_expanded).sum(1) / mask_expanded.sum(1)
        else:
            pooled = encoded.mean(1)  # (B, D)

        # Concatenate with SMT and exec signals
        signals = torch.stack([smt_signal, exec_signal], dim=-1)  # (B, 2)
        features = torch.cat([pooled, signals], dim=-1)  # (B, D+2)

        score = self.fusion(features).squeeze(-1)  # (B,)
        return score


class SimpleCodeTokenizer:
    """Simple character/word level tokenizer for code."""

    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size
        self.token_to_id = {"<pad>": 0, "<unk>": 1}
        self.id_to_token = {0: "<pad>", 1: "<unk>"}
        self._build_vocab()

    def _build_vocab(self):
        """Build vocabulary from common Python tokens."""
        python_keywords = [
            "def", "return", "if", "else", "elif", "for", "while", "in",
            "not", "and", "or", "True", "False", "None", "import", "from",
            "class", "self", "pass", "break", "continue", "lambda", "with",
            "try", "except", "finally", "raise", "yield", "assert", "del",
            "global", "nonlocal", "is", "as", "print", "len", "range",
            "list", "dict", "set", "tuple", "str", "int", "float", "bool",
            "append", "extend", "pop", "sort", "sorted", "max", "min",
            "sum", "abs", "zip", "enumerate", "map", "filter", "any", "all",
            "(", ")", "[", "]", "{", "}", ":", "=", "==", "!=", "<", ">",
            "<=", ">=", "+", "-", "*", "/", "//", "%", "**", ".", ",",
            " ", "\n", "\t", "    ", "0", "1", "2", "result", "output",
            "count", "index", "value", "i", "j", "n", "k", "s",
        ]
        idx = 2
        for tok in python_keywords:
            if tok not in self.token_to_id and idx < self.vocab_size:
                self.token_to_id[tok] = idx
                self.id_to_token[idx] = tok
                idx += 1

        # Add characters
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_":
            if c not in self.token_to_id and idx < self.vocab_size:
                self.token_to_id[c] = idx
                self.id_to_token[idx] = c
                idx += 1

    def encode(self, code: str, max_length: int = 128) -> Tuple[List[int], List[int]]:
        """Tokenize code string, return (ids, attention_mask)."""
        # Simple word-level tokenization
        import re
        tokens = re.findall(r'\w+|[^\w\s]|\s+', code)
        ids = []
        for tok in tokens:
            if tok in self.token_to_id:
                ids.append(self.token_to_id[tok])
            else:
                # Character-level fallback
                for c in tok:
                    ids.append(self.token_to_id.get(c, 1))

        # Truncate or pad
        ids = ids[:max_length]
        mask = [1] * len(ids)
        pad_len = max_length - len(ids)
        ids = ids + [0] * pad_len
        mask = mask + [0] * pad_len

        return ids, mask


def train_reward_model(
    model: VerifiabilityRewardModel,
    tokenizer: SimpleCodeTokenizer,
    training_data: List[dict],
    device: torch.device,
    epochs: int = 10,
    lr: float = 1e-3,
) -> List[float]:
    """
    Train reward model on (partial_code, smt_signal, exec_signal, label) tuples.
    Returns list of training losses.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0.0
        np.random.shuffle(training_data)

        for item in training_data:
            code = item["partial_code"]
            smt = item["smt_signal"]
            exec_s = item["exec_signal"]
            label = item["label"]

            ids, mask = tokenizer.encode(code)
            token_ids = torch.tensor([ids], dtype=torch.long).to(device)
            attention_mask = torch.tensor([mask], dtype=torch.long).to(device)
            smt_t = torch.tensor([smt], dtype=torch.float).to(device)
            exec_t = torch.tensor([exec_s], dtype=torch.float).to(device)
            label_t = torch.tensor([label], dtype=torch.float).to(device)

            optimizer.zero_grad()
            pred = model(token_ids, smt_t, exec_t, attention_mask)
            loss = F.mse_loss(pred, label_t)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(training_data) if training_data else 0.0
        losses.append(avg_loss)

    return losses


def compute_verifiability_score(
    model: VerifiabilityRewardModel,
    tokenizer: SimpleCodeTokenizer,
    partial_code: str,
    smt_signal: float,
    exec_signal: float,
    device: torch.device,
) -> float:
    """Compute verifiability potential score for a partial program."""
    model.eval()
    with torch.no_grad():
        ids, mask = tokenizer.encode(partial_code)
        token_ids = torch.tensor([ids], dtype=torch.long).to(device)
        attention_mask = torch.tensor([mask], dtype=torch.long).to(device)
        smt_t = torch.tensor([smt_signal], dtype=torch.float).to(device)
        exec_t = torch.tensor([exec_signal], dtype=torch.float).to(device)

        score = model(token_ids, smt_t, exec_t, attention_mask)
        return score.item()
