"""Orbit statistics computation and gate evaluation for H-E1."""
import logging
from typing import Any, Dict, List, Tuple

import numpy as np
from tqdm import tqdm

from weight_analysis import compute_cosine_distance, flatten_weights

logger = logging.getLogger("h-e1")


def compute_orbit_statistics(
    pairs: List[Tuple[Dict, Dict, int]],
    cosine_dist_threshold: float = 0.1,
) -> Tuple[List[Dict[str, Any]], float]:
    """Compute cosine distances and orbit candidate flags for all pairs.

    Returns (distances_list, orbit_proportion).
    Memory-efficient: flattens weights on-the-fly per pair.
    """
    distances: List[Dict[str, Any]] = []

    for idx, (m1, m2, decile) in enumerate(tqdm(pairs, desc="Computing distances")):
        w1 = flatten_weights(m1["state_dict"])
        w2 = flatten_weights(m2["state_dict"])
        dist = compute_cosine_distance(w1, w2)
        distances.append({
            "decile": decile,
            "cosine_dist": dist,
            "is_orbit_candidate": dist > cosine_dist_threshold,
        })
        if (idx + 1) % 100 == 0:
            logger.info(f"Processed {idx + 1}/{len(pairs)} pairs")

    orbit_proportion = float(np.mean([d["is_orbit_candidate"] for d in distances]))
    return distances, orbit_proportion


def per_decile_proportions(distances: List[Dict[str, Any]]) -> Dict[int, float]:
    """Return orbit candidate proportion per accuracy decile (0-9)."""
    result: Dict[int, float] = {}
    for d in range(10):
        decile_dists = [x for x in distances if x["decile"] == d]
        if decile_dists:
            result[d] = float(np.mean([x["is_orbit_candidate"] for x in decile_dists]))
        else:
            result[d] = 0.0
    return result


def evaluate_gate(
    bn_free: bool,
    orbit_proportion: float,
    threshold: float = 0.05,
) -> Dict[str, Any]:
    """Evaluate H-E1 MUST_WORK gate.

    PASS: BN-free AND orbit_proportion > threshold.
    """
    passed = bn_free and (orbit_proportion > threshold)
    return {
        "passed": passed,
        "bn_free": bn_free,
        "orbit_proportion": orbit_proportion,
        "threshold": threshold,
        "message": "PASS" if passed else "FAIL",
    }
