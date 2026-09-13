"""Git Re-Basin alignment module for H-M2."""
import torch
from typing import Dict, List, Optional, Tuple
import os
import re


def natural_sort_key(s: str):
    """Sort key for natural ordering (module_list.1 < module_list.11)."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def detect_permutable_layers(state_dict: Dict[str, torch.Tensor]) -> List[str]:
    """Return sorted conv layer names eligible for output-dim permutation.
    Only includes conv layers with direct conv->conv connections.
    """
    weight_keys = []
    sorted_keys = sorted(state_dict.keys(), key=natural_sort_key)

    for key in sorted_keys:
        tensor = state_dict[key]
        # Conv weight tensors: ndim == 4, name contains 'weight'
        if tensor.ndim == 4 and 'weight' in key.lower():
            if 'norm' not in key.lower() and 'bn' not in key.lower():
                weight_keys.append(key)

    # Filter: only include layers where output_channels == next conv's input_channels
    valid_layers = []
    for i, key in enumerate(weight_keys[:-1]):  # Exclude last conv layer
        curr_tensor = state_dict[key]
        next_key = weight_keys[i + 1]
        next_tensor = state_dict[next_key]

        curr_out_channels = curr_tensor.size(0)
        next_in_channels = next_tensor.size(1)

        if curr_out_channels == next_in_channels:
            valid_layers.append(key)

    return valid_layers


def get_next_layer(layer_name: str, state_dict: Dict[str, torch.Tensor]) -> Optional[str]:
    """Return the next weight layer name in sorted order, or None if last."""
    sorted_keys = sorted(state_dict.keys(), key=natural_sort_key)
    weight_keys = [k for k in sorted_keys if state_dict[k].ndim >= 2 and 'weight' in k.lower()
                   and 'norm' not in k.lower() and 'bn' not in k.lower()]

    try:
        idx = weight_keys.index(layer_name)
        if idx + 1 < len(weight_keys):
            return weight_keys[idx + 1]
    except ValueError:
        pass
    return None


def reorder_input_dim(w: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Reorder dim=1 (input channels) of w by perm.
    w: [out, in, ...] -> [out, in_reordered, ...]
    """
    if w.ndim == 2:
        return w[:, perm]
    elif w.ndim == 4:
        return w[:, perm, :, :]
    else:
        # Generic case
        return torch.index_select(w, dim=1, index=perm)


def shapes_compatible(model_sd: Dict[str, torch.Tensor], reference_sd: Dict[str, torch.Tensor]) -> bool:
    """Check if two models have compatible shapes for alignment."""
    for key in reference_sd.keys():
        if key not in model_sd:
            return False
        if model_sd[key].shape != reference_sd[key].shape:
            return False
    return True


def align_to_reference(
    model_sd: Dict[str, torch.Tensor],
    reference_sd: Dict[str, torch.Tensor],
    perm_layers: List[str],
    algorithm: str = "greedy",
) -> Tuple[Dict[str, torch.Tensor], bool]:
    """Align model_sd to reference_sd via weight matching.
    Returns (aligned state dict, success_flag). If shapes incompatible, returns (original, False).
    """
    # Check shape compatibility on perm_layers and next layers
    for layer_name in perm_layers:
        if layer_name not in model_sd:
            return model_sd, False
        if model_sd[layer_name].shape != reference_sd[layer_name].shape:
            return model_sd, False
        # Also check next layer
        next_layer = get_next_layer(layer_name, reference_sd)
        if next_layer:
            if next_layer not in model_sd:
                return model_sd, False
            if model_sd[next_layer].shape != reference_sd[next_layer].shape:
                return model_sd, False

    aligned_sd = {k: v.clone() for k, v in model_sd.items()}

    for layer_name in perm_layers:
        w_ref = reference_sd[layer_name].float()
        w_model = aligned_sd[layer_name].float()

        # Flatten to [out, features]
        out_dim = w_ref.size(0)
        w_ref_flat = w_ref.view(out_dim, -1)
        w_model_flat = w_model.view(out_dim, -1)

        # Normalize for correlation
        w_ref_norm = w_ref_flat / (w_ref_flat.norm(dim=1, keepdim=True) + 1e-8)
        w_model_norm = w_model_flat / (w_model_flat.norm(dim=1, keepdim=True) + 1e-8)

        # Correlation matrix: [out_ref, out_model]
        corr = torch.mm(w_ref_norm, w_model_norm.t())

        if algorithm == "greedy":
            perm = torch.argmax(corr, dim=1)
        else:
            # Hungarian algorithm
            try:
                from scipy.optimize import linear_sum_assignment
                cost = -corr.cpu().numpy()
                row_ind, col_ind = linear_sum_assignment(cost)
                perm = torch.tensor(col_ind, dtype=torch.long, device=w_model.device)
                perm = perm[torch.argsort(torch.tensor(row_ind))]
            except ImportError:
                perm = torch.argmax(corr, dim=1)

        # Apply permutation to output dimension
        aligned_sd[layer_name] = model_sd[layer_name][perm]

        # Also permute bias if exists
        bias_name = layer_name.replace('.weight', '.bias')
        if bias_name in aligned_sd:
            aligned_sd[bias_name] = model_sd[bias_name][perm]

        # Propagate to next layer's input dimension
        next_layer = get_next_layer(layer_name, model_sd)
        if next_layer is not None:
            aligned_sd[next_layer] = reorder_input_dim(aligned_sd[next_layer], perm)

    return aligned_sd, True


def verify_alignment(aligned_sd: Dict[str, torch.Tensor], reference_sd: Dict[str, torch.Tensor]) -> float:
    """Mean cosine similarity across permutable layers."""
    if not shapes_compatible(aligned_sd, reference_sd):
        return 0.0

    perm_layers = detect_permutable_layers(reference_sd)
    if not perm_layers:
        return 0.0

    sims = []
    for layer_name in perm_layers:
        a = aligned_sd[layer_name].flatten().float()
        r = reference_sd[layer_name].flatten().float()
        cos_sim = torch.dot(a, r) / (a.norm() * r.norm() + 1e-8)
        sims.append(cos_sim.item())

    return sum(sims) / len(sims)


def compute_alignment_batch(
    model_zoo: List[Dict[str, torch.Tensor]],
    reference_idx: int = 0,
    algorithm: str = "greedy",
    cache_path: Optional[str] = None,
) -> Tuple[List[Dict[str, torch.Tensor]], float]:
    """Align all models in zoo to model_zoo[reference_idx].
    Returns (aligned_zoo, convergence_rate).
    """
    # Check cache
    if cache_path and os.path.exists(cache_path):
        print(f"Loading aligned weights from cache: {cache_path}")
        cached = torch.load(cache_path, weights_only=False)
        return cached['aligned_zoo'], cached['convergence_rate']

    reference_sd = model_zoo[reference_idx]
    perm_layers = detect_permutable_layers(reference_sd)

    if not perm_layers:
        print("No permutable layers found, returning original zoo")
        return model_zoo, 1.0

    print(f"Aligning {len(model_zoo)} models to reference (idx={reference_idx})")
    print(f"Permutable layers: {perm_layers}")

    aligned_zoo = []
    convergence_count = 0
    skipped_count = 0

    for i, model_sd in enumerate(model_zoo):
        if i == reference_idx:
            aligned_zoo.append(model_sd)
            convergence_count += 1
            continue

        aligned_sd, success = align_to_reference(model_sd, reference_sd, perm_layers, algorithm)

        if not success:
            # Incompatible architecture, keep original
            aligned_zoo.append(model_sd)
            skipped_count += 1
            continue

        pre_sim = verify_alignment(model_sd, reference_sd)
        post_sim = verify_alignment(aligned_sd, reference_sd)

        if post_sim >= pre_sim:
            convergence_count += 1

        aligned_zoo.append(aligned_sd)

        if (i + 1) % 5000 == 0:
            print(f"  Aligned {i + 1}/{len(model_zoo)} models (skipped: {skipped_count})...")

    aligned_count = len(model_zoo) - skipped_count
    if aligned_count > 0:
        convergence_rate = convergence_count / aligned_count
    else:
        convergence_rate = 0.0
    print(f"Alignment convergence: {convergence_rate:.2%} ({skipped_count} skipped due to shape mismatch)")

    # Save cache
    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        torch.save({'aligned_zoo': aligned_zoo, 'convergence_rate': convergence_rate}, cache_path)
        print(f"Saved aligned weights to: {cache_path}")

    return aligned_zoo, convergence_rate
