"""
NFT Encoder (Condition A): lightweight weight-tokenization transformer for MNIST MLP zoo.
Architecture follows Zhou et al. 2023 row-tokenization scheme.
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# MNIST MLP zoo spec
ARCH = {"d_in": 784, "h": 64, "d_out": 10}
# NFT config (paper defaults)
NFT_CONFIG = {"d_model": 256, "n_heads": 8, "n_layers": 4, "dropout": 0.0}

# Token dims before projection: row tokens for W1 (784), W2 (64); bias tokens (1)
TOKEN_DIMS = {
    "W1_rows": ARCH["d_in"],   # 784 — 64 row tokens
    "b1":      1,              # 64 scalar tokens
    "W2_rows": ARCH["h"],      # 64  — 10 row tokens
    "b2":      1,              # 10 scalar tokens
}
# N_TOKENS = 64 + 64 + 10 + 10 = 148
N_TOKENS = ARCH["h"] + ARCH["h"] + ARCH["d_out"] + ARCH["d_out"]


class NFTEncoder(nn.Module):
    """
    Lightweight NFT encoder for 784→64→10 MNIST MLPs.

    Input: list of B weight dicts {"layer0.weight":(64,784), "layer0.bias":(64,),
                                    "layer1.weight":(10,64),  "layer1.bias":(10,)}
    Output: (B, d_model) mean-pooled embedding.
    """

    def __init__(self, d_model=256, n_heads=8, n_layers=4, dropout=0.0):
        super().__init__()
        self.d_model = d_model

        # Input projections for each token type
        self.proj_W1 = nn.Linear(ARCH["d_in"], d_model)   # 784 → 256
        self.proj_b1 = nn.Linear(1,            d_model)   # 1   → 256
        self.proj_W2 = nn.Linear(ARCH["h"],    d_model)   # 64  → 256
        self.proj_b2 = nn.Linear(1,            d_model)   # 1   → 256

        # Positional type embeddings (4 types) — scaled small
        self.type_embed = nn.Embedding(4, d_model)
        nn.init.normal_(self.type_embed.weight, std=0.02)

        # CLS token for pooling (avoids mean-collapse problem)
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # LayerNorm on input tokens
        self.input_norm = nn.LayerNorm(d_model)

        # Transformer encoder
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads,
            dim_feedforward=d_model * 4, dropout=dropout,
            batch_first=True, norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(enc_layer, num_layers=n_layers)

        # Property head (3 outputs: test_accuracy, gen_gap, lr)
        self.head = nn.Linear(d_model, 3)

    def _tokenize(self, weights_batch: list[dict]) -> torch.Tensor:
        """Convert list of B weight dicts → token tensor (B, N_TOKENS, d_model)."""
        B = len(weights_batch)
        device = next(self.parameters()).device

        W1 = torch.stack([w["layer0.weight"] for w in weights_batch]).to(device)  # (B, 64, 784)
        b1 = torch.stack([w["layer0.bias"]   for w in weights_batch]).to(device)  # (B, 64)
        W2 = torch.stack([w["layer1.weight"] for w in weights_batch]).to(device)  # (B, 10, 64)
        b2 = torch.stack([w["layer1.bias"]   for w in weights_batch]).to(device)  # (B, 10)

        # Project each token type to d_model
        tok_W1 = self.proj_W1(W1)                    # (B, 64, d_model)
        tok_b1 = self.proj_b1(b1.unsqueeze(-1))      # (B, 64, d_model)
        tok_W2 = self.proj_W2(W2)                    # (B, 10, d_model)
        tok_b2 = self.proj_b2(b2.unsqueeze(-1))      # (B, 10, d_model)

        # Type embeddings (broadcast)
        t = self.type_embed.weight  # (4, d_model)
        tok_W1 = tok_W1 + t[0]
        tok_b1 = tok_b1 + t[1]
        tok_W2 = tok_W2 + t[2]
        tok_b2 = tok_b2 + t[3]

        # Concatenate: (B, 64+64+10+10, d_model) = (B, 148, d_model)
        tokens = torch.cat([tok_W1, tok_b1, tok_W2, tok_b2], dim=1)
        return tokens

    def encode(self, weights_batch: list[dict]) -> torch.Tensor:
        """Extract CLS-token embedding. Returns (B, d_model)."""
        tokens = self._tokenize(weights_batch)          # (B, 148, d_model)
        tokens = self.input_norm(tokens)
        B = tokens.shape[0]
        cls = self.cls_token.expand(B, -1, -1)          # (B, 1, d_model)
        tokens = torch.cat([cls, tokens], dim=1)        # (B, 149, d_model)
        out    = self.transformer(tokens)               # (B, 149, d_model)
        emb    = out[:, 0]                              # (B, d_model) CLS token
        return emb

    def forward(self, weights_batch: list[dict]) -> torch.Tensor:
        """Returns property predictions (B, 3) — used during training."""
        emb = self.encode(weights_batch)
        return self.head(emb)


def build_nft(d_model=256, n_heads=8, n_layers=4, dropout=0.0) -> NFTEncoder:
    return NFTEncoder(d_model=d_model, n_heads=n_heads, n_layers=n_layers, dropout=dropout)


def load_nft_encoder(checkpoint_path: str, device: str = "cpu") -> NFTEncoder:
    """Load NFT from checkpoint. Raises FileNotFoundError if missing."""
    import os
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"NFT checkpoint not found: {checkpoint_path}\n"
            "Run FR-0.3 training fallback."
        )
    model = build_nft()
    state = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    print(f"NFT loaded from {checkpoint_path}")
    return model


def extract_embeddings(
    nft_encoder: NFTEncoder,
    weights_list: list[dict],
    batch_size: int = 64,
    device: str = "cpu",
) -> torch.Tensor:
    """Batched embedding extraction. Returns (N, d_model) on CPU."""
    nft_encoder.eval()
    all_embs = []
    with torch.no_grad():
        for i in range(0, len(weights_list), batch_size):
            batch = weights_list[i:i + batch_size]
            emb = nft_encoder.encode(batch)  # (B, d_model)
            all_embs.append(emb.cpu())
    return torch.cat(all_embs, dim=0)  # (N, d_model)
