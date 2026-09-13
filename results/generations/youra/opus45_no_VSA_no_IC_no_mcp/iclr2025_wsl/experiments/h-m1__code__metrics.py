from typing import Dict, List
import numpy as np
from scipy.stats import wasserstein_distance


def attention_entropy(attn_weights) -> float:
    """Compute entropy of attention distribution."""
    import torch
    if isinstance(attn_weights, torch.Tensor):
        attn_weights = attn_weights.detach().cpu().numpy()
    attn_mean = np.mean(attn_weights, axis=(0, 1))
    eps = 1e-8
    return float(-np.sum(attn_mean * np.log(attn_mean + eps)))


def layer_activation_variance(activations: List) -> float:
    """Compute variance across layer activations (locality measure)."""
    import torch
    if len(activations) == 0:
        return 0.0
    norms = [act.norm().item() if isinstance(act, torch.Tensor) else np.linalg.norm(act) for act in activations]
    return float(np.var(norms))


def wasserstein_grad_distance(dws_norms: List[float], nft_norms: List[float]) -> float:
    """Compute Wasserstein distance between gradient norm distributions."""
    if len(dws_norms) == 0 or len(nft_norms) == 0:
        return 0.0
    return wasserstein_distance(dws_norms, nft_norms)


def weight_update_cov(layer_updates: Dict[str, List[float]]) -> float:
    """Coefficient of variation of weight updates across layers (std/mean)."""
    if not layer_updates:
        return 0.0
    # Get final epoch updates for each layer
    final_updates = [updates[-1] for updates in layer_updates.values() if updates]
    if len(final_updates) == 0:
        return 0.0
    mean = np.mean(final_updates)
    if mean < 1e-10:
        return 0.0
    return float(np.std(final_updates) / mean)


def locality_score(layer_updates: Dict[str, List[float]], epoch: int = -1) -> float:
    """DWS locality score: higher = more localized (varied) updates across layers."""
    if not layer_updates:
        return 0.0
    updates_at_epoch = [updates[epoch] for updates in layer_updates.values() if len(updates) > abs(epoch)]
    if len(updates_at_epoch) == 0:
        return 0.0
    mean = np.mean(updates_at_epoch)
    if mean < 1e-10:
        return 0.0
    return float(np.std(updates_at_epoch) / mean * 100)


def check_success_criteria(dws_stats: Dict, nft_stats: Dict, cfg) -> Dict[str, bool]:
    """Check h-m1 MECHANISM success criteria."""
    results = {}

    # Criterion 1: DWS shows different gradient flow than NFT (Wasserstein > 0.1)
    dws_all_grads = []
    nft_all_grads = []
    for v in dws_stats.get("grad_norms", {}).values():
        dws_all_grads.extend(v)
    for v in nft_stats.get("grad_norms", {}).values():
        nft_all_grads.extend(v)
    w_dist = wasserstein_grad_distance(dws_all_grads, nft_all_grads)
    results["gradient_flow_different"] = w_dist > cfg.wasserstein_threshold
    results["wasserstein_distance"] = w_dist

    # Criterion 2: DWS weight updates more localized (higher CoV)
    dws_cov = weight_update_cov(dws_stats.get("weight_updates", {}))
    nft_cov = weight_update_cov(nft_stats.get("weight_updates", {}))
    results["dws_more_localized"] = dws_cov > nft_cov
    results["dws_cov"] = dws_cov
    results["nft_cov"] = nft_cov

    # Criterion 3: NFT attention entropy increases (becomes more distributed)
    nft_entropy = nft_stats.get("attention_entropy", [])
    if len(nft_entropy) >= 2:
        results["nft_entropy_increases"] = nft_entropy[-1] > nft_entropy[0]
        results["nft_entropy_start"] = nft_entropy[0]
        results["nft_entropy_end"] = nft_entropy[-1]
    else:
        results["nft_entropy_increases"] = False
        results["nft_entropy_start"] = 0.0
        results["nft_entropy_end"] = 0.0

    # Criterion 4: Signatures detectable within first 20 epochs
    early_epoch = min(cfg.early_signature_epoch, len(dws_all_grads) // max(1, len(dws_stats.get("grad_norms", {1:1}))))
    dws_early = dws_all_grads[:early_epoch * len(dws_stats.get("grad_norms", {1:1}))] if dws_all_grads else []
    nft_early = nft_all_grads[:early_epoch * len(nft_stats.get("grad_norms", {1:1}))] if nft_all_grads else []
    early_w_dist = wasserstein_grad_distance(dws_early, nft_early) if dws_early and nft_early else 0.0
    results["early_signature_detected"] = early_w_dist > cfg.wasserstein_threshold * 0.5
    results["early_wasserstein"] = early_w_dist

    # Overall PASS
    results["all_criteria_pass"] = all([
        results["gradient_flow_different"],
        results["dws_more_localized"],
        results["nft_entropy_increases"],
        results["early_signature_detected"]
    ])

    return results
