"""Per-stratum ECE and ΔECE computation for H-M1."""
import logging
import sys
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


def _get_compute_ece():
    """Import compute_ece from h-e1 via sys.path injection."""
    from config import H_E1_CODE_PATH
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    try:
        from evaluation.ece import compute_ece
        return compute_ece
    except ImportError as e:
        raise ImportError(
            f"Cannot import compute_ece from H-E1. Check H_E1_CODE_PATH={H_E1_CODE_PATH}. Error: {e}"
        )


def compute_stratum_ece(
    cache: dict,
    mask: np.ndarray,
    n_bins: int = 15,
) -> float:
    """
    ECE for masked subset. Delegates to h-e1 compute_ece.
    cache: {"conf": (N,) float32, "correct": (N,) int, ...}
    mask:  (N,) bool — high-preservation stratum selector
    """
    conf = cache["conf"][mask]
    correct = cache["correct"][mask]
    if len(conf) == 0:
        raise ValueError("Empty stratum — mask selects zero examples")
    compute_ece = _get_compute_ece()
    return compute_ece(conf, correct, n_bins)


def compute_delta_ece(stratum_ece: float, clean_ece: float = 0.279) -> float:
    """ΔECE = stratum_ece - clean_ece. Positive = calibration gap vs clean."""
    return stratum_ece - clean_ece


def run_all_strata(
    caches: dict,
    clean_ece: float = 0.279,
    n_bins: int = 15,
) -> dict:
    """
    Per-split ECE + ΔECE.
    Returns {split: {"ece": float, "delta_ece": float, "n": int}}.
    """
    results = {}
    for split, cache in caches.items():
        try:
            n = len(cache["conf"])
            mask = np.ones(n, dtype=bool)
            ece = compute_stratum_ece(cache, mask, n_bins)
            delta = compute_delta_ece(ece, clean_ece)
            results[split] = {"ece": ece, "delta_ece": delta, "n": n}
            logger.info("[%s] ECE=%.4f ΔECE=%.4f n=%d", split, ece, delta, n)
        except ValueError as e:
            logger.error("Skipping split '%s': %s", split, e)
    return results


def check_anli_gradient(stratum_results: dict) -> bool:
    """Returns True if ΔECE(anli_r3) >= ΔECE(anli_r2) >= ΔECE(anli_r1)."""
    r1 = stratum_results.get("anli_r1", {}).get("delta_ece")
    r2 = stratum_results.get("anli_r2", {}).get("delta_ece")
    r3 = stratum_results.get("anli_r3", {}).get("delta_ece")
    if any(x is None for x in [r1, r2, r3]):
        logger.warning("ANLI gradient check: missing round(s) r1=%s r2=%s r3=%s", r1, r2, r3)
        return False
    result = r3 >= r2 >= r1
    logger.info("ANLI gradient check: r1=%.4f r2=%.4f r3=%.4f -> %s", r1, r2, r3, result)
    return result
