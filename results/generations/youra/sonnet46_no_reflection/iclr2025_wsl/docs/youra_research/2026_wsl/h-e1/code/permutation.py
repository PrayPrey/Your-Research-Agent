"""
Canonical channel permutation for CNN and Transformer checkpoints.
Implements S_{c_in} x S_{c_out} per layer for CNNs, and S_h head permutation for Transformers.
"""
import copy
from typing import Optional
import torch
from torch import Tensor


def _make_perm(size: int, seed: int) -> Tensor:
    """Returns random permutation index tensor of shape [size], dtype=torch.long."""
    g = torch.Generator()
    g.manual_seed(seed)
    return torch.randperm(size, generator=g)


def _permute_linear(
    weight: Tensor,
    bias: Optional[Tensor],
    pi_out: Tensor,
    pi_in: Tensor,
) -> tuple:
    """Returns (permuted_weight [c_out, c_in], permuted_bias [c_out])."""
    w_perm = weight[pi_out][:, pi_in]
    b_perm = bias[pi_out] if bias is not None else None
    return w_perm, b_perm


def _permute_conv2d(
    weight: Tensor,
    bias: Optional[Tensor],
    pi_out: Tensor,
    pi_in: Tensor,
) -> tuple:
    """Returns (permuted_weight [c_out, c_in, H, W], permuted_bias [c_out])."""
    w_perm = weight[pi_out][:, pi_in]
    b_perm = bias[pi_out] if bias is not None else None
    return w_perm, b_perm


def _permute_batchnorm(
    state_dict: dict,
    bn_prefix: str,
    pi_out: Tensor,
) -> dict:
    """Permutes running_mean, running_var, weight, bias of BN by pi_out."""
    result = {}
    for suffix in ["running_mean", "running_var", "weight", "bias"]:
        key = f"{bn_prefix}.{suffix}"
        if key in state_dict:
            result[key] = state_dict[key][pi_out]
    return result


def _permute_layernorm(
    state_dict: dict,
    ln_prefix: str,
    pi: Tensor,
) -> dict:
    """Permutes LayerNorm weight and bias by pi."""
    result = {}
    for suffix in ["weight", "bias"]:
        key = f"{ln_prefix}.{suffix}"
        if key in state_dict:
            result[key] = state_dict[key][pi]
    return result


def _is_weight_key(key: str) -> bool:
    return key.endswith(".weight") and "running" not in key and "num_batches" not in key


def _is_bn_key(key: str) -> bool:
    return any(x in key for x in ["bn", "batch_norm", "batchnorm", "norm"])


def _get_bn_prefix(key: str) -> str:
    return key.rsplit(".", 1)[0]


def apply_canonical_channel_permutation(
    state_dict: dict,
    perm_seed: int,
) -> dict:
    """
    Apply S_{c_in} x S_{c_out} per layer to CNN/Linear state_dict.
    Propagates bias by pi_out; propagates BN by pi_out of preceding layer.
    Returns a new state_dict (does not modify input).
    """
    result = copy.deepcopy(state_dict)

    # Collect weight keys in order (skip BN/running stats)
    weight_keys = [k for k in state_dict.keys() if _is_weight_key(k)]

    pi_prev_out = None  # pi_out of previous layer (used as pi_in for next)

    n_layers = len(weight_keys)

    for i, key in enumerate(weight_keys):
        w = state_dict[key]
        if w.dim() < 2:
            # e.g. 1D weight (embedding, LN) — skip channel permutation
            pi_prev_out = None
            continue

        c_out = w.shape[0]
        c_in = w.shape[1]

        is_last = (i == n_layers - 1)

        # pi_in: propagated from previous layer's pi_out
        # First layer: use identity for input channels (don't permute network input)
        # Subsequent layers: propagate pi_out of previous layer
        # Handle Flatten: if prev layer had n_ch channels and this layer has n_ch * spatial inputs,
        # expand the permutation (each channel block of `spatial` neurons moves together)
        if pi_prev_out is None:
            # First layer — identity for input channels
            pi_in = torch.arange(c_in, dtype=torch.long)
        elif len(pi_prev_out) == c_in:
            pi_in = pi_prev_out
        elif c_in % len(pi_prev_out) == 0:
            # Conv→Linear via Flatten: expand channel perm to flattened spatial indices
            spatial = c_in // len(pi_prev_out)
            expanded = []
            for ch in pi_prev_out:
                for s in range(spatial):
                    expanded.append(ch.item() * spatial + s)
            pi_in = torch.tensor(expanded, dtype=torch.long)
        else:
            pi_in = torch.arange(c_in, dtype=torch.long)

        if is_last:
            # Last layer: only permute input channels (pi_in), output channels are class indices
            # Use identity for pi_out so predictions don't change
            pi_out = torch.arange(c_out)
        else:
            pi_out = _make_perm(c_out, perm_seed + i * 2)

        if w.dim() == 4:
            w_perm, b_perm = _permute_conv2d(w, state_dict.get(key.replace("weight", "bias")), pi_out, pi_in)
        else:
            w_perm, b_perm = _permute_linear(w, state_dict.get(key.replace("weight", "bias")), pi_out, pi_in)

        result[key] = w_perm
        bias_key = key.replace("weight", "bias")
        if bias_key in result and b_perm is not None:
            result[bias_key] = b_perm

        # Look for BN/LN after this layer and permute it
        keys_list = list(state_dict.keys())
        key_idx = keys_list.index(key)
        # Check next few keys for BN suffix
        for j in range(key_idx + 1, min(key_idx + 5, len(keys_list))):
            next_key = keys_list[j]
            if next_key.endswith(".running_mean") or (
                "bn" in next_key.lower() and next_key.endswith(".weight")
            ):
                bn_prefix = next_key.rsplit(".", 1)[0]
                bn_updates = _permute_batchnorm(state_dict, bn_prefix, pi_out)
                result.update(bn_updates)
                break

        pi_prev_out = pi_out

    return result


def apply_transformer_head_permutation(
    state_dict: dict,
    perm_seed: int,
    n_heads: int,
    head_dim: int = None,
) -> dict:
    """
    Apply S_h head permutation to Transformer MultiheadAttention.
    Handles both fused in_proj_weight and separate Q/K/V projections.
    Returns a new state_dict.
    """
    result = copy.deepcopy(state_dict)
    pi_heads = _make_perm(n_heads, perm_seed)

    # Detect architecture: fused in_proj or separate q/k/v projections
    keys = list(state_dict.keys())

    # Check for separate Q/K/V (Transformer-NFN style: queries/keys/values)
    qkv_prefixes = []
    for k in keys:
        if any(k.endswith(f"{proj}.weight") for proj in [
            "queries", "keys", "values", "q_proj", "k_proj", "v_proj",
            "query", "key", "value"
        ]):
            prefix = k.rsplit(".", 1)[0]
            qkv_prefixes.append((k, prefix))

    if qkv_prefixes:
        # Separate Q/K/V projections: apply head permutation to each
        for weight_key, prefix in qkv_prefixes:
            w = state_dict[weight_key]  # [d_model, d_model] or [head_dim*n_heads, d_model]
            if w.dim() == 2:
                d_out, d_in = w.shape
                if head_dim is None:
                    head_dim_inferred = d_out // n_heads
                else:
                    head_dim_inferred = head_dim

                if d_out == n_heads * head_dim_inferred:
                    # Reshape to [n_heads, head_dim, d_in], permute heads, reshape back
                    w_3d = w.view(n_heads, head_dim_inferred, d_in)
                    w_3d = w_3d[pi_heads]
                    result[weight_key] = w_3d.view(d_out, d_in)

                    bias_key = weight_key.replace("weight", "bias")
                    if bias_key in state_dict:
                        b = state_dict[bias_key]  # [d_out]
                        if b.shape[0] == n_heads * head_dim_inferred:
                            b_3d = b.view(n_heads, head_dim_inferred)
                            b_3d = b_3d[pi_heads]
                            result[bias_key] = b_3d.view(d_out)

        # Handle out_projection weight [d_model, d_model]
        for k in keys:
            if "out_proj" in k or "out_projection" in k:
                if k.endswith(".weight"):
                    w = state_dict[k]  # [d_model, d_model]
                    d_out, d_in = w.shape
                    if head_dim is None:
                        head_dim_inferred = d_in // n_heads
                    else:
                        head_dim_inferred = head_dim
                    if d_in == n_heads * head_dim_inferred:
                        # Reshape to [d_out, n_heads, head_dim], permute head dim
                        w_3d = w.view(d_out, n_heads, head_dim_inferred)
                        w_3d = w_3d[:, pi_heads, :]
                        result[k] = w_3d.view(d_out, d_in)

    else:
        # Fused in_proj_weight [3*d_model, d_model]
        for k in keys:
            if "in_proj_weight" in k:
                w = state_dict[k]  # [3*d_model, d_model]
                d_model = w.shape[0] // 3
                if head_dim is None:
                    head_dim_inferred = d_model // n_heads
                else:
                    head_dim_inferred = head_dim

                # Split Q, K, V
                q, k_w, v = w[:d_model], w[d_model:2*d_model], w[2*d_model:]
                # Reshape each to [n_heads, head_dim, d_model]
                def perm_block(block):
                    b3d = block.view(n_heads, head_dim_inferred, d_model)
                    return b3d[pi_heads].view(d_model, d_model)

                result[k] = torch.cat([perm_block(q), perm_block(k_w), perm_block(v)], dim=0)

                # Handle in_proj_bias
                bias_k = k.replace("weight", "bias")
                if bias_k in state_dict:
                    b = state_dict[bias_k]  # [3*d_model]
                    bq, bk, bv = b[:d_model], b[d_model:2*d_model], b[2*d_model:]
                    def perm_bias(bb):
                        b3d = bb.view(n_heads, head_dim_inferred)
                        return b3d[pi_heads].view(d_model)
                    result[bias_k] = torch.cat([perm_bias(bq), perm_bias(bk), perm_bias(bv)])

            if "out_proj.weight" in k:
                w = state_dict[k]
                d_out, d_model = w.shape
                if head_dim is None:
                    head_dim_inferred = d_model // n_heads
                else:
                    head_dim_inferred = head_dim
                if d_model == n_heads * head_dim_inferred:
                    w_3d = w.view(d_out, n_heads, head_dim_inferred)
                    w_3d = w_3d[:, pi_heads, :]
                    result[k] = w_3d.view(d_out, d_model)

    return result
