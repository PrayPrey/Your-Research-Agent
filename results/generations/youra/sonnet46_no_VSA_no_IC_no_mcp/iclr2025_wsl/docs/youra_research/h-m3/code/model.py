"""H-M3 model: CanonicalWeightEncoder wrapping NFTEncoder."""
import sys
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))
from nft_encoder import NFTEncoder, build_nft  # noqa: E402
from data_loader import SPLITS  # noqa: E402

from data_prep import CONDITION_FNS  # noqa: E402

SPLITS_LIST = [50176, 64, 640, 10]  # W1, b1, W2, b2; sum=50890


def flat_to_weight_dicts(X_flat: np.ndarray, device: torch.device) -> list:
    """Convert (N, 51850) numpy array to list of N weight dicts for NFTEncoder."""
    result = []
    for row in X_flat:
        t = torch.tensor(row, dtype=torch.float32)
        parts = torch.split(t, SPLITS_LIST)
        result.append({
            "layer0.weight": parts[0].reshape(64, 784).to(device),
            "layer0.bias":   parts[1].to(device),
            "layer1.weight": parts[2].reshape(10, 64).to(device),
            "layer1.bias":   parts[3].to(device),
        })
    return result


class CanonicalWeightEncoder(nn.Module):
    """
    Apply condition preprocessing then NFT encoding + regression head.
    Input: weights_flat (batch, 51850) float32 numpy or tensor
    Output: predictions (batch, 3) float32
    """

    def __init__(self, condition: str = 'D', embed_dim: int = 256,
                 n_layers: int = 4, nhead: int = 8, dim_feedforward: int = 512,
                 dropout: float = 0.1):
        super().__init__()
        self.condition = condition
        self.nft_encoder = build_nft(d_model=embed_dim, n_heads=nhead,
                                     n_layers=n_layers, dropout=dropout)
        self.regressor = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 3),
        )

    @property
    def device(self):
        return next(self.parameters()).device

    def forward(self, weights_flat):
        """
        weights_flat: (B, 51850) tensor or numpy array
        Returns: (B, 3)
        """
        if isinstance(weights_flat, torch.Tensor):
            X_np = weights_flat.cpu().numpy()
        else:
            X_np = weights_flat

        # Apply canonicalization
        condition_fn = CONDITION_FNS[self.condition]
        X_canon = condition_fn(X_np)

        # Convert to weight dicts
        weight_dicts = flat_to_weight_dicts(X_canon, self.device)

        # NFT encode
        emb = self.nft_encoder.encode(weight_dicts)  # (B, embed_dim)
        return self.regressor(emb)

    def freeze_encoder(self):
        for p in self.nft_encoder.parameters():
            p.requires_grad_(False)

    def unfreeze_encoder(self):
        for p in self.nft_encoder.parameters():
            p.requires_grad_(True)
