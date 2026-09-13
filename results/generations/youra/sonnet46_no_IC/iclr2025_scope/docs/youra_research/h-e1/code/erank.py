from __future__ import annotations
import json
import math
from pathlib import Path

import torch


def compute_erank(W: torch.Tensor, eps: float = 1e-10) -> float:
    """erank(W) = exp(H(σ/‖σ‖₁)), σ = singular values. fp32 only."""
    W = W.float()
    S = torch.linalg.svdvals(W)
    S = S[S > eps]
    if S.numel() == 0:
        return 1.0
    p = S / S.sum()
    H = -(p * p.log()).sum()
    return math.exp(H.item())


def compute_erank_map(model_name: str) -> dict[str, float]:
    """
    Load pretrained base model, iterate 2D weight matrices,
    skip embeddings and norms. Returns {param_name: erank}.
    Expected: ≥60 entries per model.
    """
    from transformers import AutoModel, AutoConfig

    print(f"  Loading {model_name} for erank computation...")
    # Use base AutoModel (no task head) — only weight matrices needed
    model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float32)
    model.eval()

    erank_map: dict[str, float] = {}
    with torch.no_grad():
        for name, param in model.named_parameters():
            if param.dim() != 2:
                continue
            # Skip embedding and norm layers
            lower = name.lower()
            if any(skip in lower for skip in ["embed", "norm", "layernorm", "ln_"]):
                continue
            erank_map[name] = compute_erank(param.data)

    print(f"  erank_map: {len(erank_map)} entries")
    return erank_map


def save_erank_map(erank_map: dict[str, float], path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(erank_map, indent=2))


def load_erank_map(path: Path) -> dict[str, float]:
    return json.loads(Path(path).read_text())
