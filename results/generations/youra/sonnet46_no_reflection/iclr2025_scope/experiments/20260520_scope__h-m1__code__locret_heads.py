"""
H-M1 Locret Retaining Heads: CIS formula S̃ = σ([Q,K,V] @ W1) @ W2
W1 ∈ R^{6144×1024}, W2 ∈ R^{1024×8}
"""
import torch
import torch.nn as nn
from huggingface_hub import hf_hub_download
from config import ExperimentConfig


class RetainingHead(nn.Module):
    def __init__(self, fc1_weight: torch.Tensor, fc2_weight: torch.Tensor):
        super().__init__()
        # fc1: (cis_input_dim, locret_hidden) = (6144, 1024)
        self.fc1 = nn.Linear(fc1_weight.shape[1], fc1_weight.shape[0], bias=False)
        self.fc1.weight = nn.Parameter(fc1_weight.clone().float())
        # fc2: (num_kv_heads, locret_hidden) = (8, 1024)
        self.fc2 = nn.Linear(fc2_weight.shape[1], fc2_weight.shape[0], bias=False)
        self.fc2.weight = nn.Parameter(fc2_weight.clone().float())

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
        # q: (B, L, hidden_size=4096), k/v: (B, L, num_kv_heads*head_dim=1024)
        qkv = torch.cat([q, k, v], dim=-1).float()  # (B, L, 6144)
        hidden = torch.sigmoid(qkv @ self.fc1.weight.T)  # (B, L, 1024)
        cis = hidden @ self.fc2.weight.T                  # (B, L, 8)
        return cis


class LocretHeadCollection(nn.Module):
    def __init__(self, heads: list):
        super().__init__()
        self.heads = nn.ModuleList(heads)

    def __len__(self):
        return len(self.heads)

    def __getitem__(self, idx):
        return self.heads[idx]


def load_locret_heads(config: ExperimentConfig, device: str = "cpu") -> LocretHeadCollection:
    import os
    checkpoint_path = hf_hub_download(
        repo_id=config.locret_checkpoint,
        filename="llama-3.1-8B-instruct.bin",
    )
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)

    heads = []
    for i in range(config.num_layers):
        fc1_key = f"model.layers.{i}.self_attn.fc1.weight"
        fc2_key = f"model.layers.{i}.self_attn.fc2.weight"
        if fc1_key not in state:
            # Try alternate key format
            fc1_key = f"layers.{i}.self_attn.fc1.weight"
            fc2_key = f"layers.{i}.self_attn.fc2.weight"
        fc1_w = state[fc1_key]   # (1024, 6144)
        fc2_w = state[fc2_key]   # (8, 1024)
        head = RetainingHead(fc1_w, fc2_w)
        for p in head.parameters():
            p.requires_grad = True
        heads.append(head)

    collection = LocretHeadCollection(heads)
    return collection.to(device)


def freeze_locret_heads(collection: LocretHeadCollection) -> None:
    for p in collection.parameters():
        p.requires_grad = False
