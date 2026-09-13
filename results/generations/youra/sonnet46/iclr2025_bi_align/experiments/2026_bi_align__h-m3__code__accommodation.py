"""
accommodation.py - C_sem computation and OLS residualization.

h-m1 extension: compute_tier_csem_matrix() computes C_sem per tier.
h-m2 extension: compute_bidirectional_csem_per_tier() computes both H<-A and A<-H per tier.
                compute_h_given_a_csem_array() and compute_a_given_h_csem_array() per-pair helpers.
"""
import logging
import numpy as np
import statsmodels.api as sm
from typing import List, Dict, Callable, Optional

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
    """Compute OLS residuals of cos_array regressed on covariate."""
    X = sm.add_constant(covariate)
    model = sm.OLS(cos_array, X)
    result = model.fit()
    return result.resid


def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float:
    """Compute C_sem = mean(cos_actual) - mean(cos_random)."""
    return float(np.mean(cos_actual) - np.mean(cos_random))


def apply_residualization(
    cos_dict: Dict[str, np.ndarray],
    token_counts: List[int],
    jaccard_overlaps: List[float],
) -> Dict[str, np.ndarray]:
    """Apply OLS residualization: first token length, then lexical overlap."""
    tc = np.array(token_counts, dtype=np.float64)
    jac = np.array(jaccard_overlaps, dtype=np.float64)

    result = {}
    for key, cos_arr in cos_dict.items():
        res1 = residualize(cos_arr.astype(np.float64), tc)
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
    """Compute C_sem per tier for one SBERT model (h-m1 function, unchanged).

    Args:
        tier_pairs: Dict mapping tier_name -> {h_next, a_actual, h_prompt, ...}
        embedder: Embedder instance with encode_tier() method
        controls_fn_random: Function(ai_emb, seed) -> random_emb
        controls_fn_topic: Function(prompt_emb, ai_emb) -> topic_emb
        seed: Random seed for reproducibility

    Returns:
        Dict mapping tier_name -> {c_sem, cos_actual_mean, cos_random_mean,
                                    raw_cos_actual, raw_cos_random, n_pairs}
    """
    results = {}
    for tier in TIER_ORDER:
        pairs = tier_pairs[tier]
        n_pairs = len(pairs["h_next"])

        h_emb = embedder.encode_tier(pairs["h_next"], prefix="h", tier=tier, n_pairs=n_pairs)
        a_emb = embedder.encode_tier(pairs["a_actual"], prefix="a", tier=tier, n_pairs=n_pairs)
        p_emb = embedder.encode_tier(pairs["h_prompt"], prefix="p", tier=tier, n_pairs=n_pairs)

        a_random = controls_fn_random(a_emb, seed=seed)
        a_topic = controls_fn_topic(p_emb, a_emb)

        cos_dict = compute_cosine_similarities(h_emb, a_emb, a_topic, a_random)
        c_sem = compute_c_sem(cos_dict["cos_actual"], cos_dict["cos_random"])

        logger.info(f"Tier {tier} C_sem computed: {c_sem:.4f}")

        results[tier] = {
            "c_sem": c_sem,
            "cos_actual_mean": float(np.mean(cos_dict["cos_actual"])),
            "cos_random_mean": float(np.mean(cos_dict["cos_random"])),
            "raw_cos_actual": cos_dict["cos_actual"],
            "raw_cos_random": cos_dict["cos_random"],
            "n_pairs": n_pairs,
        }

    return results


def aggregate_model_results(all_model_results: Dict) -> Dict:
    """Create summary matrix [models × tiers] of C_sem values."""
    csem_matrix = {}
    for model_slug, tier_results in all_model_results.items():
        csem_matrix[model_slug] = {
            tier: tier_results[tier]["c_sem"]
            for tier in TIER_ORDER if tier in tier_results
        }

    mean_csem_per_tier = {}
    for tier in TIER_ORDER:
        vals = [csem_matrix[m][tier] for m in csem_matrix if tier in csem_matrix[m]]
        mean_csem_per_tier[tier] = float(np.mean(vals)) if vals else 0.0

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


# ============================================================================
# H-M2 EXTENSIONS: Bidirectional C_sem computation
# ============================================================================

def compute_h_given_a_csem_array(
    emb_h_next: np.ndarray,
    emb_a_curr: np.ndarray,
    emb_a_shuffle: np.ndarray,
) -> np.ndarray:
    """Per-pair C_sem^H<-A = cos(H_{t+1}, A_t) - cos(H_{t+1}, A_t[shuffle]).

    Uses dot product of L2-normalized vectors as cosine similarity.

    Args:
        emb_h_next: [N, D] L2-normalized H_{t+1} embeddings
        emb_a_curr: [N, D] L2-normalized A_t embeddings
        emb_a_shuffle: [N, D] topic-matched shuffle of A_curr

    Returns:
        np.ndarray of shape [N,] - per-pair C_sem^H<-A differences
    """
    cos_actual = np.sum(emb_h_next * emb_a_curr, axis=1)      # [N,]
    cos_shuffle = np.sum(emb_h_next * emb_a_shuffle, axis=1)   # [N,]
    return cos_actual - cos_shuffle


def compute_a_given_h_csem_array(
    emb_a_next: np.ndarray,
    emb_h_curr: np.ndarray,
    emb_h_shuffle: np.ndarray,
) -> np.ndarray:
    """Per-pair C_sem^A<-H = cos(A_{t+1}, H_t) - cos(A_{t+1}, H_t[shuffle_A]).

    Uses dot product of L2-normalized vectors as cosine similarity.

    Args:
        emb_a_next: [N, D] L2-normalized A_{t+1} embeddings
        emb_h_curr: [N, D] L2-normalized H_t embeddings
        emb_h_shuffle: [N, D] topic-matched shuffle of H_curr

    Returns:
        np.ndarray of shape [N,] - per-pair C_sem^A<-H differences
    """
    cos_actual = np.sum(emb_a_next * emb_h_curr, axis=1)      # [N,]
    cos_shuffle = np.sum(emb_a_next * emb_h_shuffle, axis=1)   # [N,]
    return cos_actual - cos_shuffle


def compute_bidirectional_csem_per_tier(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,
    controls_fn_topic: Callable,
    ipw_weights: Optional[Dict[str, np.ndarray]] = None,
    seed: int = 42,
) -> Dict[str, Dict]:
    """Compute both H<-A and A<-H C_sem per tier. Logs [FR-M2] prefix.

    For each tier in TIER_ORDER:
      H<-A: cos(H_{t+1}, A_t) - cos(H_{t+1}, A_t[shuffle_H])
      A<-H: cos(A_{t+1}, H_t) - cos(A_{t+1}, H_t[shuffle_A])

    Args:
        tier_pairs: Dict mapping tier_name -> {h_next, a_actual, h_prompt,
                                               h_curr, a_next, ...}
        embedder: Embedder instance with encode_tier() method
        controls_fn_random: Function(emb, seed) -> random_emb
        controls_fn_topic: Function(prompt_emb, partner_emb) -> topic_emb (n_jobs=1)
        ipw_weights: Optional IPW weights per tier for weighted mean
        seed: Random seed

    Returns:
        {tier: {
            csem_H_given_A: float,
            csem_A_given_H: float,
            csem_H_given_A_array: np.ndarray [N,],
            csem_A_given_H_array: np.ndarray [N,],
            raw_cos_H_given_A: np.ndarray [N,],
            raw_cos_A_given_H: np.ndarray [N,],
            n_pairs: int,
        }}
    """
    results = {}

    for tier in TIER_ORDER:
        pairs = tier_pairs[tier]
        n_pairs = len(pairs["h_next"])

        # H<-A direction (reuse h-m1 encoding pattern)
        emb_h_next = embedder.encode_tier(pairs["h_next"], prefix="h", tier=tier, n_pairs=n_pairs)
        emb_a_curr = embedder.encode_tier(pairs["a_actual"], prefix="a", tier=tier, n_pairs=n_pairs)
        emb_p = embedder.encode_tier(pairs["h_prompt"], prefix="p", tier=tier, n_pairs=n_pairs)

        # Topic-matched shuffle for H<-A: shuffle A_curr using prompt as anchor
        emb_a_shuffle = controls_fn_topic(emb_p, emb_a_curr)  # n_jobs=1 CRITICAL
        h_given_a = compute_h_given_a_csem_array(emb_h_next, emb_a_curr, emb_a_shuffle)

        # A<-H direction (new for h-m2)
        a_next_texts = pairs.get("a_next", [])
        h_curr_texts = pairs.get("h_curr", pairs["h_prompt"])

        # Filter pairs where a_next is empty (no next AI turn)
        valid_mask = np.array([bool(a) for a in a_next_texts])
        if valid_mask.sum() == 0:
            # No valid a_next — use zeros for A<-H
            logger.warning(f"[FR-M2] Tier {tier}: no a_next available, A<-H set to 0")
            a_given_h = np.zeros(n_pairs, dtype=np.float32)
            emb_a_next_full = np.zeros((n_pairs, emb_h_next.shape[1]), dtype=np.float32)
            emb_h_curr_full = emb_h_next  # placeholder
        else:
            # Encode A_next using full list (empty strings get zero embeddings after masking)
            emb_a_next_full = embedder.encode_tier(
                [t if t else "." for t in a_next_texts],
                prefix="a_next", tier=tier, n_pairs=n_pairs
            )
            emb_h_curr_full = embedder.encode_tier(
                h_curr_texts if h_curr_texts else pairs["h_prompt"],
                prefix="h_curr", tier=tier, n_pairs=n_pairs
            )

            # Topic-matched shuffle for A<-H: shuffle H_curr using prompt as anchor
            emb_h_shuffle = controls_fn_topic(emb_p, emb_h_curr_full)  # n_jobs=1 CRITICAL
            a_given_h = compute_a_given_h_csem_array(emb_a_next_full, emb_h_curr_full, emb_h_shuffle)

        # Apply IPW weights if provided
        if ipw_weights and tier in ipw_weights:
            w = ipw_weights[tier]  # [N,]
            csem_H = float(np.sum(w * h_given_a))
            csem_A = float(np.sum(w * a_given_h))
        else:
            csem_H = float(np.mean(h_given_a))
            csem_A = float(np.mean(a_given_h))

        logger.info(f"[FR-M2] Tier {tier}: C_sem^H<-A={csem_H:.4f}, C_sem^A<-H={csem_A:.4f}")

        results[tier] = {
            "csem_H_given_A": csem_H,
            "csem_A_given_H": csem_A,
            "csem_H_given_A_array": h_given_a,
            "csem_A_given_H_array": a_given_h,
            "raw_cos_H_given_A": np.sum(emb_h_next * emb_a_curr, axis=1),
            "raw_cos_A_given_H": np.sum(emb_a_next_full * emb_h_curr_full, axis=1),
            "n_pairs": n_pairs,
        }

    return results
