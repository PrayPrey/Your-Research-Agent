"""
accommodation.py - C_sem computation and OLS residualization.

h-m1 extension: compute_tier_csem_matrix() computes C_sem per tier.
"""
import logging
import numpy as np
import statsmodels.api as sm
from typing import List, Dict, Callable

logger = logging.getLogger(__name__)

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]


def compute_cosine_similarities(
    h_next: np.ndarray,
    a_actual: np.ndarray,
    a_topic: np.ndarray,
    a_random: np.ndarray,
) -> Dict[str, np.ndarray]:
    """Compute elementwise cosine similarities (dot product for L2-normalized vectors).

    Args:
        h_next: shape (N, D) - next human turn embeddings (L2-normalized)
        a_actual: shape (N, D) - actual AI response embeddings (L2-normalized)
        a_topic: shape (N, D) - topic-matched control embeddings
        a_random: shape (N, D) - random control embeddings

    Returns:
        dict with keys 'cos_actual', 'cos_topic', 'cos_random', each shape (N,)
    """
    cos_actual = np.sum(h_next * a_actual, axis=1)
    cos_topic = np.sum(h_next * a_topic, axis=1)
    cos_random = np.sum(h_next * a_random, axis=1)
    return {
        "cos_actual": cos_actual,
        "cos_topic": cos_topic,
        "cos_random": cos_random,
    }


def residualize(cos_array: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    """Compute OLS residuals of cos_array regressed on covariate.

    Args:
        cos_array: shape (N,) - dependent variable
        covariate: shape (N,) - covariate to regress out

    Returns:
        Residuals of shape (N,).
    """
    X = sm.add_constant(covariate)
    model = sm.OLS(cos_array, X)
    result = model.fit()
    return result.resid


def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float:
    """Compute C_sem = mean(cos_actual) - mean(cos_random).

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_random: shape (N,) - random control cosine similarities

    Returns:
        C_sem scalar float.
    """
    return float(np.mean(cos_actual) - np.mean(cos_random))


def apply_residualization(
    cos_dict: Dict[str, np.ndarray],
    token_counts: List[int],
    jaccard_overlaps: List[float],
) -> Dict[str, np.ndarray]:
    """Apply OLS residualization: first token length, then lexical overlap.

    Args:
        cos_dict: dict with 'cos_actual', 'cos_topic', 'cos_random'
        token_counts: list of token counts for each pair
        jaccard_overlaps: list of jaccard overlaps for each pair

    Returns:
        New dict with residualized cosine arrays.
    """
    tc = np.array(token_counts, dtype=np.float64)
    jac = np.array(jaccard_overlaps, dtype=np.float64)

    result = {}
    for key, cos_arr in cos_dict.items():
        # Step 1: residualize on token counts
        res1 = residualize(cos_arr.astype(np.float64), tc)
        # Step 2: residualize on jaccard overlaps
        res2 = residualize(res1, jac)
        result[key] = res2.astype(np.float32)

    return result


def compute_tier_csem_matrix(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,
    controls_fn_topic: Callable,
    seed: int = 42,
) -> Dict[str, Dict]:
    """Compute C_sem per tier for one SBERT model.

    For each tier in TIER_ORDER:
      1. Encode h_next, a_actual, h_prompt with tier-namespaced cache keys
      2. Build random control (shuffle)
      3. Build topic control (KNN)
      4. Compute cosine similarities and C_sem
      5. Log: "Tier {tier} C_sem computed: {c_sem:.4f}" (FR-E3)

    Args:
        tier_pairs: Dict mapping tier_name -> {h_next, a_actual, h_prompt, ...}
        embedder: Embedder instance with encode_tier() method
        controls_fn_random: Function(ai_emb, seed) -> random_emb (build_random_control)
        controls_fn_topic: Function(prompt_emb, ai_emb) -> topic_emb (build_topic_control)
        seed: Random seed for reproducibility

    Returns:
        Dict mapping tier_name -> {c_sem, cos_actual_mean, cos_random_mean,
                                    raw_cos_actual, raw_cos_random, n_pairs}
    """
    results = {}
    for tier in TIER_ORDER:
        pairs = tier_pairs[tier]
        n_pairs = len(pairs["h_next"])

        # Step 1-3: Encode with tier-namespaced cache keys
        h_emb = embedder.encode_tier(pairs["h_next"], prefix="h", tier=tier, n_pairs=n_pairs)
        a_emb = embedder.encode_tier(pairs["a_actual"], prefix="a", tier=tier, n_pairs=n_pairs)
        p_emb = embedder.encode_tier(pairs["h_prompt"], prefix="p", tier=tier, n_pairs=n_pairs)

        # Step 4: Build controls
        a_random = controls_fn_random(a_emb, seed=seed)
        a_topic = controls_fn_topic(p_emb, a_emb)

        # Step 5: Compute cosines
        cos_dict = compute_cosine_similarities(h_emb, a_emb, a_topic, a_random)
        c_sem = compute_c_sem(cos_dict["cos_actual"], cos_dict["cos_random"])

        # FR-E3: Log per-tier C_sem
        logger.info(f"Tier {tier} C_sem computed: {c_sem:.4f}")

        results[tier] = {
            "c_sem": c_sem,
            "cos_actual_mean": float(np.mean(cos_dict["cos_actual"])),
            "cos_random_mean": float(np.mean(cos_dict["cos_random"])),
            "raw_cos_actual": cos_dict["cos_actual"],   # Full array for J-T test
            "raw_cos_random": cos_dict["cos_random"],   # Full array
            "n_pairs": n_pairs,
        }

    return results


def aggregate_model_results(all_model_results: Dict) -> Dict:
    """Create summary matrix [models × tiers] of C_sem values.

    Args:
        all_model_results: {model_slug: {tier: {c_sem, ...}}}

    Returns:
        {
            'csem_matrix': {model_slug: {tier: c_sem}},
            'mean_csem_per_tier': {tier: mean_across_models},
            'tier_order_consistent': bool (all models show T1 < T2 < T3 direction)
        }
    """
    csem_matrix = {}
    for model_slug, tier_results in all_model_results.items():
        csem_matrix[model_slug] = {
            tier: tier_results[tier]["c_sem"]
            for tier in TIER_ORDER if tier in tier_results
        }

    # Mean C_sem per tier across all models
    mean_csem_per_tier = {}
    for tier in TIER_ORDER:
        vals = [csem_matrix[m][tier] for m in csem_matrix if tier in csem_matrix[m]]
        mean_csem_per_tier[tier] = float(np.mean(vals)) if vals else 0.0

    # Check if all models show monotonically increasing trend T1 < T2 < T3
    tier_order_consistent = True
    for model_slug, tier_csem in csem_matrix.items():
        if len(tier_csem) == 3:
            vals = [tier_csem.get(t, None) for t in TIER_ORDER]
            if None not in vals:
                if not (vals[0] < vals[1] < vals[2]):
                    tier_order_consistent = False

    return {
        "csem_matrix": csem_matrix,
        "mean_csem_per_tier": mean_csem_per_tier,
        "tier_order_consistent": tier_order_consistent,
    }
