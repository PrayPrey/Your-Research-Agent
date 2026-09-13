"""Ablation studies for H-M1."""
import logging
import sys
import numpy as np

logger = logging.getLogger(__name__)


def _compute_ece(conf, correct, n_bins=15):
    from config import H_E1_CODE_PATH
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    from evaluation.ece import compute_ece
    return compute_ece(conf, correct, n_bins)


def ablation_criterion_sensitivity(
    caches: dict,
    clean_ece: float = 0.279,
    n_bins: int = 15,
) -> dict:
    """
    Variant A: all examples pooled (no stratification)
    Variant B: advglue_mnli only
    Variant C: anli R1/R2/R3 separately
    Returns {"variant_A": delta, "variant_B": delta,
             "variant_C_r1": delta, "variant_C_r2": delta, "variant_C_r3": delta}
    """
    results = {}

    # Variant A — pool all splits (skip None)
    conf_parts, correct_parts = [], []
    for cache in caches.values():
        if cache is None:
            continue
        conf_parts.append(cache["conf"])
        correct_parts.append(cache["correct"])
    if conf_parts:
        pool_conf = np.concatenate(conf_parts)
        pool_correct = np.concatenate(correct_parts)
        results["variant_A"] = _compute_ece(pool_conf, pool_correct, n_bins) - clean_ece
    else:
        results["variant_A"] = None
        logger.warning("Variant A: no caches available")

    # Variant B — AdvGLUE only
    cache_b = caches.get("advglue_mnli")
    if cache_b is not None:
        results["variant_B"] = _compute_ece(cache_b["conf"], cache_b["correct"], n_bins) - clean_ece
    else:
        results["variant_B"] = None
        logger.warning("Variant B: advglue_mnli cache missing")

    # Variant C — ANLI per round
    for r in [1, 2, 3]:
        key = f"anli_r{r}"
        cache_r = caches.get(key)
        if cache_r is not None:
            results[f"variant_C_r{r}"] = _compute_ece(cache_r["conf"], cache_r["correct"], n_bins) - clean_ece
        else:
            results[f"variant_C_r{r}"] = None
            logger.warning("Variant C r%d: %s cache missing", r, key)

    return results


def ablation_bin_count(
    cache: dict,
    mask: np.ndarray,
    bin_counts: tuple = (10, 15, 20),
    clean_eces: dict = None,
) -> dict:
    """Returns {n_bins: ece} for the masked stratum."""
    conf = cache["conf"][mask]
    correct = cache["correct"][mask]
    return {b: _compute_ece(conf, correct, b) for b in bin_counts}


def ablation_task_scope(
    caches: dict,
    clean_ece: float = 0.279,
    n_bins: int = 15,
) -> dict:
    """
    NLI only vs NLI + QQP + SST-2.
    Returns {"nli_only": {"ece": float, "delta_ece": float},
             "nli_qqp_sst2": {"ece": float, "delta_ece": float}}
    """
    nli_splits = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]
    all_splits = nli_splits + ["advglue_qqp", "advglue_sst2"]

    def pool_and_compute(splits):
        conf_parts, correct_parts = [], []
        for sp in splits:
            c = caches.get(sp)
            if c is None:
                logger.debug("ablation_task_scope: skip missing split '%s'", sp)
                continue
            conf_parts.append(c["conf"])
            correct_parts.append(c["correct"])
        if not conf_parts:
            return None, None
        pc = np.concatenate(conf_parts)
        pr = np.concatenate(correct_parts)
        ece = _compute_ece(pc, pr, n_bins)
        return ece, ece - clean_ece

    nli_ece, nli_delta = pool_and_compute(nli_splits)
    all_ece, all_delta = pool_and_compute(all_splits)

    return {
        "nli_only":    {"ece": nli_ece, "delta_ece": nli_delta},
        "nli_qqp_sst2": {"ece": all_ece, "delta_ece": all_delta},
    }
