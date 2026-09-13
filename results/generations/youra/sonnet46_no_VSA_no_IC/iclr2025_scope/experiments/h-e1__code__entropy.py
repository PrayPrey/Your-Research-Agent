"""Entropy computation for h-e1: per-layer attention entropy."""
import numpy as np
import torch


def compute_layer_entropy(model, input_ids, eps=1e-9):
    """
    Single forward pass with output_attentions=True.

    Args:
        model: LlamaForCausalLM with attn_implementation='eager'
        input_ids: (1, seq_len) tensor on model device
        eps: stability term for log

    Returns:
        entropy_per_layer: (n_layers,) mean Shannon entropy per layer
    """
    with torch.no_grad():
        output = model(input_ids, output_attentions=True)

    n_layers = len(output.attentions)
    entropy_per_layer = np.zeros(n_layers, dtype=np.float64)

    for layer_idx in range(n_layers):
        attn = output.attentions[layer_idx]  # (1, 32, seq_len, seq_len)
        attn_np = attn.squeeze(0).float().cpu().numpy()  # (32, seq_len, seq_len)
        del attn

        # Shannon entropy: H[h, q] = -sum_k attn[h,q,k] * log(attn[h,q,k] + eps)
        H = -np.sum(attn_np * np.log(attn_np + eps), axis=-1)  # (32, seq_len)
        entropy_per_layer[layer_idx] = H.mean()

        del attn_np, H

    return entropy_per_layer  # (n_layers,)


def score_subset(model, sequences, eps=1e-9, verbose=True):
    """
    Run compute_layer_entropy() for each sequence, return mean.

    Args:
        model: LlamaForCausalLM with attn_implementation='eager'
        sequences: list of (1, 2048) tensors
        eps: stability term
        verbose: print progress every 10 sequences

    Returns:
        (n_layers,) mean entropy over all sequences
    """
    all_entropies = []
    for i, input_ids in enumerate(sequences):
        input_ids = input_ids.to(next(model.parameters()).device)
        layer_ent = compute_layer_entropy(model, input_ids, eps=eps)
        all_entropies.append(layer_ent)
        if verbose and (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(sequences)} sequences")

    return np.mean(all_entropies, axis=0)  # (n_layers,)
