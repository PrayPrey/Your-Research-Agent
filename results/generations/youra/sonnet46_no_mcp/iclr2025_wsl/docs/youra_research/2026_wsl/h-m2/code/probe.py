"""NFN permutation sensitivity probing for H-M2."""
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
from tqdm import tqdm

logger = logging.getLogger("h-m2")

# Type alias
LayerOrder = List[Tuple[str, str, int]]


def get_mnist_cnn_layer_order() -> LayerOrder:
    """Return permutation spec for Conv(32)-Conv(64)-FC(128)-FC(10) MNIST-CNN.

    Each tuple: (outgoing_weight_key, incoming_weight_key, n_neurons)
    State dict uses module_list.{idx}.weight keys from Schurholt zoo.
    """
    # Actual hyp_rand architecture: Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10)
    # Keys verified from dataset: module_list.{0,3,6,9,11}
    return [
        ("module_list.0.weight", "module_list.3.weight", 8),    # conv1(8) -> conv2
        ("module_list.3.weight", "module_list.6.weight", 6),    # conv2(6) -> conv3
        ("module_list.6.weight", "module_list.9.weight", 4),    # conv3(4) -> fc1
        ("module_list.9.weight", "module_list.11.weight", 20),  # fc1(20) -> fc2
    ]


def _permute_conv_out(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute conv output channels. weight: [C_out, C_in, kH, kW]"""
    return weight[perm]


def _permute_conv_in(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute conv input channels. weight: [C_out, C_in, kH, kW]"""
    return weight[:, perm, :, :]


def _permute_fc_out(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute FC output rows. weight: [N_out, N_in]"""
    return weight[perm]


def _permute_fc_in(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute FC input cols. weight: [N_out, N_in]"""
    return weight[:, perm]


def generate_permuted_weights(
    state_dict: Dict[str, torch.Tensor],
    layer_order: LayerOrder,
    seed: Optional[int] = None,
) -> Dict[str, torch.Tensor]:
    """Apply random neuron permutation preserving functional equivalence.

    For each (out_key, in_key, n) in layer_order:
    - Permute out_key dim-0 and its bias
    - Permute in_key dim-1 (handles conv->fc spatial reshape)
    """
    rng = torch.Generator()
    if seed is not None:
        rng.manual_seed(seed)

    new_sd = {k: v.clone() for k, v in state_dict.items()}

    for (out_key, in_key, n) in layer_order:
        if out_key not in new_sd or in_key not in new_sd:
            logger.warning(f"Key not found: {out_key} or {in_key}, skipping")
            continue

        perm = torch.randperm(n, generator=rng)

        # Permute outgoing weight dim-0
        w_out = new_sd[out_key]
        if w_out.dim() == 4:
            new_sd[out_key] = _permute_conv_out(w_out, perm)
        else:
            new_sd[out_key] = _permute_fc_out(w_out, perm)

        # Permute corresponding bias
        bias_key = out_key.replace("weight", "bias")
        if bias_key in new_sd:
            new_sd[bias_key] = new_sd[bias_key][perm]

        # Permute incoming weight dim-1 (with conv->fc spatial reshape)
        w_in = new_sd[in_key]
        if w_in.dim() == 4:
            # Conv layer: permute input channels
            new_sd[in_key] = _permute_conv_in(w_in, perm)
        else:
            # FC layer: may need spatial reshape for conv->fc boundary
            n_out, n_in = w_in.shape
            if n_in % n == 0:
                spatial = n_in // n
                w_reshaped = w_in.view(n_out, n, spatial)
                w_reshaped = w_reshaped[:, perm, :]
                new_sd[in_key] = w_reshaped.view(n_out, n_in)
            else:
                new_sd[in_key] = _permute_fc_in(w_in, perm)

    return new_sd


def _embed_nfn(
    encoder,
    state_dict: Dict[str, torch.Tensor],
    weight_key_order: List[str],
    device: torch.device,
) -> torch.Tensor:
    """Extract ordered weight list from state_dict and encode with NFNEncoder.

    No mean/std normalization — NFN operates on raw weight tensors.
    Returns: [embed_dim] on CPU.
    """
    weight_list = [
        state_dict[k].float().cpu().unsqueeze(0).to(device)  # [1, *shape]
        for k in weight_key_order
    ]
    encoder.eval()
    with torch.no_grad():
        emb = encoder(weight_list)  # [1, embed_dim]
    return emb.squeeze(0).cpu()  # [embed_dim]


def compute_permutation_sensitivity_nfn(
    encoder,
    checkpoints: List[Dict],
    weight_key_order: List[str],
    cfg,
    device: torch.device,
) -> Dict:
    """Compute NFN permutation sensitivity score.

    sensitivity_score = mean(L2(enc(w), enc(perm(w)))) / mean(L2(enc(w_i), enc(w_j)))
    Reuses generate_permuted_weights from h-m1/code/probe.py.
    Reuses stratified_pair_sample from h-e1/code/weight_analysis.py.
    """
    # Import h-e1 utilities
    he1_code = Path(__file__).parent.parent.parent / "h-e1" / "code"
    if str(he1_code) not in sys.path:
        sys.path.insert(0, str(he1_code))
    from weight_analysis import stratified_pair_sample  # type: ignore

    layer_order = get_mnist_cnn_layer_order()

    n_per_decile = max(cfg.n_pairs // 10, 5)
    pairs = stratified_pair_sample(
        checkpoints,
        n_per_decile=n_per_decile,
        acc_threshold=cfg.acc_threshold,
        seed=cfg.seed,
    )

    if len(pairs) < cfg.min_pairs:
        raise RuntimeError(
            f"Only {len(pairs)} pairs found, need at least {cfg.min_pairs}"
        )

    logger.info(
        f"[H-M2] Running NFN permutation sensitivity probing on {len(pairs)} pairs..."
    )

    equiv_dists = []
    random_dists = []
    decile_equiv: Dict[int, List[float]] = {}
    decile_random: Dict[int, List[float]] = {}

    encoder.eval()
    with torch.no_grad():
        for (ckpt_i, ckpt_j, decile) in tqdm(pairs, desc="NFN Probing"):
            # Equiv pair: original vs permuted version of same model
            e_orig = _embed_nfn(encoder, ckpt_i["state_dict"], weight_key_order, device)
            perm_sd = generate_permuted_weights(
                ckpt_i["state_dict"], layer_order, seed=cfg.seed
            )
            e_perm = _embed_nfn(encoder, perm_sd, weight_key_order, device)
            d_equiv = torch.norm(e_orig - e_perm).item()
            equiv_dists.append(d_equiv)

            # Random pair: two different models
            e_j = _embed_nfn(encoder, ckpt_j["state_dict"], weight_key_order, device)
            d_random = torch.norm(e_orig - e_j).item()
            random_dists.append(d_random)

            if decile not in decile_equiv:
                decile_equiv[decile] = []
                decile_random[decile] = []
            decile_equiv[decile].append(d_equiv)
            decile_random[decile].append(d_random)

    mean_equiv = float(np.mean(equiv_dists))
    mean_random = float(np.mean(random_dists))
    sensitivity_score = mean_equiv / (mean_random + 1e-8)

    # Per-decile sensitivity scores (equiv/random ratio per decile)
    decile_scores = [
        float(np.mean(decile_equiv.get(d, [0.0])) / (np.mean(decile_random.get(d, [1.0])) + 1e-8))
        for d in range(10)
    ]

    logger.info(
        f"[H-M2] sensitivity_score={sensitivity_score:.4f}, "
        f"mean_equiv_L2={mean_equiv:.4f}, mean_random_L2={mean_random:.4f}"
    )

    return {
        "sensitivity_score": sensitivity_score,
        "mean_equiv_L2": mean_equiv,
        "mean_random_L2": mean_random,
        "n_pairs": len(pairs),
        "equiv_dists": equiv_dists,
        "random_dists": random_dists,
        "decile_scores": decile_scores,
    }
