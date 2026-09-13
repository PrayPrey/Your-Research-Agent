from typing import List

import torch
import torch.nn as nn
from torch import Tensor


def attention_entropy(attn_weights: Tensor) -> float:
    attn = attn_weights.mean(dim=(0, 1))
    attn = attn / (attn.sum(dim=-1, keepdim=True) + 1e-8)
    entropy = -(attn * torch.log(attn + 1e-8)).sum(dim=-1).mean()
    return entropy.item()


def layer_activation_variance(layer_outputs: List[Tensor]) -> float:
    variances = []
    for feat in layer_outputs:
        var = feat.var(dim=0).mean()
        variances.append(var)
    mean_var = torch.stack(variances).mean()
    return mean_var.item()


def verify_mechanism(model: nn.Module, sample_input: List[Tensor], model_type: str) -> bool:
    if model_type == "dws":
        feats = model.get_layer_activations(sample_input)
        score = layer_activation_variance(feats)
        return score < 1.0
    elif model_type == "nft":
        attn = model.get_attention_weights(sample_input)
        entropy = attention_entropy(attn)
        return entropy > 2.0
    else:
        raise ValueError(f"unknown model_type: {model_type}")
