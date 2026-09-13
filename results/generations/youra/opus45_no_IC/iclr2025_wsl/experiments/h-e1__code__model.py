import torch
import torch.nn as nn
from typing import Any


class NFNRegressor(nn.Module):
    """Permutation-equivariant NFN for predicting model accuracy from weights."""

    def __init__(self, network_spec: Any, nfn_channels: int = 32):
        super().__init__()
        from nfn import layers

        self.nfn = nn.Sequential(
            layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.HNPPool(network_spec),
            nn.Flatten(start_dim=-2),
            nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
        )

    def forward(self, wsfeat: Any) -> torch.Tensor:
        return self.nfn(wsfeat)


class MLPMatched(nn.Module):
    """MLP baseline with matched parameter count."""

    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3):
        super().__init__()
        layers_list = [nn.Linear(input_dim, hidden_dim), nn.ReLU()]
        for _ in range(num_layers - 2):
            layers_list.extend([nn.Linear(hidden_dim, hidden_dim), nn.ReLU()])
        layers_list.append(nn.Linear(hidden_dim, 1))
        self.net = nn.Sequential(*layers_list)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def flatten_weights(wsfeat: Any) -> torch.Tensor:
    """Flatten WeightSpaceFeatures to (B, D) tensor."""
    all_tensors = []
    for w in wsfeat.weights:
        all_tensors.append(w.flatten(start_dim=1))
    for b in wsfeat.biases:
        all_tensors.append(b.flatten(start_dim=1))
    return torch.cat(all_tensors, dim=1)


def count_params(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_flat_dim(models: list) -> int:
    """Get flattened weight dimension from models."""
    sample_sd = models[0]['state_dict']
    total = 0
    for v in sample_sd.values():
        total += v.numel()
    return total
