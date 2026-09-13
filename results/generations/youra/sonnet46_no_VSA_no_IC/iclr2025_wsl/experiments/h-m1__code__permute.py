import re
import torch
from collections import OrderedDict
from torch import Tensor


def _sorted_weight_keys(weight_dict: dict) -> list:
    """Sort weight keys numerically by embedded integers (handles module_list.11 > module_list.3)."""
    keys = [k for k in weight_dict if k.endswith(".weight")]
    return sorted(keys, key=lambda k: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', k)])


def permute_weights(weight_dict: dict, layer_key: str, perm: Tensor) -> OrderedDict:
    """Permute neuron ordering of one hidden layer.

    Permutes rows of layer_key weight (and bias), cols of the next weight layer.
    Handles 2D (linear) and 4D (conv) weights.
    Returns new OrderedDict (original unchanged).
    """
    result = OrderedDict((k, v.clone()) for k, v in weight_dict.items())
    bias_key = layer_key.replace(".weight", ".bias")
    all_weight_keys = _sorted_weight_keys(weight_dict)
    try:
        idx = all_weight_keys.index(layer_key)
        next_weight_key = all_weight_keys[idx + 1] if idx + 1 < len(all_weight_keys) else None
    except ValueError:
        next_weight_key = None

    w_in = result[layer_key]
    if w_in.dim() == 2:
        result[layer_key] = w_in[perm, :]
    elif w_in.dim() == 4:
        result[layer_key] = w_in[perm, :, :, :]

    if bias_key in result:
        result[bias_key] = result[bias_key][perm]

    if next_weight_key is not None:
        w_out = result[next_weight_key]
        if w_out.dim() == 2:
            result[next_weight_key] = w_out[:, perm]
        elif w_out.dim() == 4:
            result[next_weight_key] = w_out[:, perm, :, :]

    return result


def permute_all_hidden_layers(weight_dict: dict, hidden_keys: list, perm: Tensor) -> OrderedDict:
    """Apply permutation to all hidden layers (independent perm per layer if sizes differ)."""
    result = weight_dict
    for layer_key in hidden_keys:
        hidden_size = weight_dict[layer_key].shape[0]
        if perm.shape[0] != hidden_size:
            layer_perm = torch.randperm(hidden_size)
        else:
            layer_perm = perm
        result = permute_weights(result, layer_key, layer_perm)
    return result


def get_perm(size: int, device=torch.device("cpu")) -> Tensor:
    return torch.randperm(size, device=device)
