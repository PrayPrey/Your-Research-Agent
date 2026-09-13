import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from collections import OrderedDict

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


class DeepSetsEncoder(nn.Module):
    """Permutation-invariant encoder via sum pooling (Zaheer et al. 2017).
    Treats each weight tensor (flattened per-layer) as one set element.
    """

    def __init__(self, element_dim: int, phi_hidden: int, rho_hidden: int, embed_dim: int = 128):
        super().__init__()
        self.phi = nn.Sequential(
            nn.Linear(element_dim, phi_hidden),
            nn.ReLU(),
            nn.Linear(phi_hidden, phi_hidden),
            nn.ReLU(),
        )
        self.rho = nn.Sequential(
            nn.Linear(phi_hidden, rho_hidden),
            nn.ReLU(),
            nn.Linear(rho_hidden, embed_dim),
        )
        self.embed_dim = embed_dim

    def forward(self, x_elements: torch.Tensor) -> torch.Tensor:
        # x_elements: (B, N_layers, element_dim)
        B, N, D = x_elements.shape
        # Apply phi elementwise
        phi_out = self.phi(x_elements.view(B * N, D)).view(B, N, -1)  # (B, N, phi_hidden)
        # Sum pool over N
        pooled = phi_out.sum(dim=1)  # (B, phi_hidden)
        # Apply rho
        embedding = self.rho(pooled)  # (B, embed_dim)
        return embedding


class DeepSetsWithHead(nn.Module):
    """DeepSetsEncoder + Linear(embed_dim, 1) prediction head."""

    def __init__(self, encoder: DeepSetsEncoder, embed_dim: int = 128):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Linear(embed_dim, 1)

    def forward(self, x_elements: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x_elements: (B, N_layers, element_dim)
        embedding = self.encoder(x_elements)   # (B, embed_dim)
        prediction = self.head(embedding)       # (B, 1)
        return embedding, prediction


def grid_search_deep_sets(
    element_dim: int,
    phi_hidden_candidates: List[int],
    rho_hidden: int,
    embed_dim: int,
    target_min: int,
    target_max: int,
) -> Tuple[DeepSetsEncoder, int, int]:
    """Grid search phi_hidden to hit [target_min, target_max] params.
    Returns: (encoder, phi_hidden, param_count)
    """
    best_encoder = None
    best_phi = None
    best_n = None
    best_dist = float("inf")

    for phi_hidden in phi_hidden_candidates:
        encoder = DeepSetsEncoder(element_dim, phi_hidden, rho_hidden, embed_dim)
        n_params = count_params(encoder)
        logger.info(f"  phi_hidden={phi_hidden}: {n_params:,} params")
        if target_min <= n_params <= target_max:
            logger.info(f"  ✓ Selected phi_hidden={phi_hidden} ({n_params:,} params)")
            return encoder, phi_hidden, n_params
        dist = min(abs(n_params - target_min), abs(n_params - target_max))
        if dist < best_dist:
            best_dist = dist
            best_encoder = encoder
            best_phi = phi_hidden
            best_n = n_params

    logger.warning(f"No phi_hidden in {phi_hidden_candidates} hits [{target_min},{target_max}]. "
                   f"Using closest: phi_hidden={best_phi} ({best_n:,} params)")
    return best_encoder, best_phi, best_n


def _import_hm1_models(cfg):
    import importlib.util
    hm1_models = Path(cfg.hm1_code_dir).resolve() / "models.py"
    spec = importlib.util.spec_from_file_location("hm1_models", str(hm1_models))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_hm2_models(cfg):
    import importlib.util
    hm2_models = Path(cfg.hm2_code_dir).resolve() / "models.py"
    spec = importlib.util.spec_from_file_location("hm2_models", str(hm2_models))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_flat_mlp_checkpoint(cfg, input_dim: int, hidden_dims: List[int] = None) -> "FlatMLPWithHead":
    """Load h-m1 trained checkpoint. Falls back to retraining if missing."""
    hm1 = _import_hm1_models(cfg)
    FlatMLPEncoder = hm1.FlatMLPEncoder
    FlatMLPWithHead = hm1.FlatMLPWithHead

    if hidden_dims is None:
        hidden_dims = [193]

    encoder = FlatMLPEncoder(input_dim=input_dim, hidden_dims=hidden_dims, embed_dim=cfg.embed_dim)
    model = FlatMLPWithHead(encoder, embed_dim=cfg.embed_dim)

    ckpt_path = Path(cfg.hm1_code_dir) / "results" / "best_flat_mlp_encoder.pt"
    if not ckpt_path.exists():
        logger.warning(f"FlatMLP checkpoint not found at {ckpt_path}. Returning untrained model.")
        return model

    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
    elif isinstance(ckpt, (dict, OrderedDict)):
        # Check if keys match model state dict
        model_keys = set(model.state_dict().keys())
        ckpt_keys = set(ckpt.keys())
        if ckpt_keys <= model_keys or len(ckpt_keys & model_keys) > len(ckpt_keys) * 0.8:
            state = ckpt
        else:
            # Try as raw state dict anyway
            state = ckpt
    else:
        state = ckpt

    try:
        model.load_state_dict(state, strict=True)
        logger.info(f"FlatMLP checkpoint loaded from {ckpt_path}")
    except Exception as e:
        logger.warning(f"strict load failed ({e}), trying non-strict")
        model.load_state_dict(state, strict=False)

    return model


def load_nfn_checkpoint(cfg, weight_shapes: List[tuple],
                        channel_dim: int = 112, n_layers: int = 3) -> "NFNWithHead":
    """Load h-m2 trained checkpoint. Falls back to untrained if missing."""
    hm2 = _import_hm2_models(cfg)
    NFNEncoder = hm2.NFNEncoder
    NFNWithHead = hm2.NFNWithHead

    encoder = NFNEncoder(weight_shapes=weight_shapes, channel_dim=channel_dim,
                         embed_dim=cfg.embed_dim, n_layers=n_layers)
    model = NFNWithHead(encoder, embed_dim=cfg.embed_dim)

    ckpt_path = Path(cfg.hm2_code_dir) / "results" / "best_nfn_encoder.pt"
    if not ckpt_path.exists():
        logger.warning(f"NFN checkpoint not found at {ckpt_path}. Returning untrained model.")
        return model

    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)

    model.encoder.load_state_dict(ckpt["encoder_state"], strict=True)
    model.head.load_state_dict(ckpt["head_state"], strict=True)
    logger.info(f"NFN checkpoint loaded from {ckpt_path} (epoch={ckpt.get('epoch','?')})")

    return model
