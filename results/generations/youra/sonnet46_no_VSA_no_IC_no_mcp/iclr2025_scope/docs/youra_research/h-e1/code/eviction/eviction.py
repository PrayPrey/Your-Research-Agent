import logging
import torch

logger = logging.getLogger(__name__)


def _cache_to_layer_list(past_key_values):
    """Extract list of (k, v) tensors from DynamicCache or tuple-of-tuples."""
    try:
        # transformers 5.x DynamicCache: iterate yields (keys, values, ...)
        layers = []
        for item in past_key_values:
            k, v = item[0], item[1]
            layers.append((k, v))
        return layers
    except Exception:
        return list(past_key_values)


def _rebuild_cache(layer_list, original_cache):
    """Rebuild a DynamicCache (or tuple) from modified (k, v) layer list."""
    try:
        from transformers.cache_utils import DynamicCache
        if isinstance(original_cache, DynamicCache):
            return DynamicCache(ddp_cache_data=[(k, v) for k, v in layer_list])
    except ImportError:
        pass
    return tuple(layer_list)


def apply_kv_eviction(
    past_key_values,
    scores: list,
    retention_ratio: float = 0.5,
    log_details: bool = True,
) -> object:
    """
    Evict bottom (1 - retention_ratio) KV positions per head per layer.
    scores: list of L tensors, each (B, H, S)
    Returns evicted cache in same format as input.
    """
    layers = _cache_to_layer_list(past_key_values)
    evicted_layers = []

    for l, (k, v) in enumerate(layers):
        S = k.shape[2]
        keep_n = max(1, int(S * retention_ratio))

        sc = scores[l]
        # Ensure scores on same device as k
        if sc.device != k.device:
            sc = sc.to(k.device)
        # Handle head broadcast (M6 may be shape (1,1,S) or (1,32,S))
        if sc.shape[1] != k.shape[1]:
            sc = sc.expand(k.shape[0], k.shape[1], sc.shape[2])
        # Ensure float for topk
        if sc.dtype != torch.float32:
            sc = sc.float()

        topk_idx = sc.topk(keep_n, dim=-1).indices      # (B, H, K)
        topk_idx = topk_idx.sort(dim=-1).values          # preserve causal order
        idx = topk_idx.unsqueeze(-1).expand(-1, -1, -1, k.shape[-1])  # (B, H, K, D)

        k_ret = k.gather(2, idx)
        v_ret = v.gather(2, idx)
        evicted_layers.append((k_ret, v_ret))

        if log_details and l == 0:
            logger.info(f"KV eviction applied: retained {keep_n}/{S} per head (layer {l})")

    return _rebuild_cache(evicted_layers, past_key_values)


def verify_mechanism_activated(
    kv_before,
    kv_after,
    results_m1: dict,
    results_m0: dict,
    retention_ratio: float = 0.5,
) -> tuple:
    before_layers = _cache_to_layer_list(kv_before)
    after_layers = _cache_to_layer_list(kv_after)

    S_full = before_layers[0][0].shape[2]
    K = after_layers[0][0].shape[2]
    expected_K = int(S_full * retention_ratio)

    indicators = {
        "shape_changed": K == expected_K,
        "shape_reduced": K < S_full,
        "m1_non_zero": results_m1.get("macro_f1", 0) > 0,
        "m1_differs_from_m0": abs(results_m1.get("macro_f1", 0) - results_m0.get("macro_f1", 0)) > 0.1,
    }

    all_pass = all(indicators.values())
    if all_pass:
        logger.info(f"✅ Mechanism verified: KV reduced {S_full} → {K} per head per layer")
    else:
        failed = [k for k, v in indicators.items() if not v]
        logger.warning(f"⚠️ Mechanism checks failed: {failed}")

    return all_pass, indicators
