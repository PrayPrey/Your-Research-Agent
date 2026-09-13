"""
delta_probe.py - Three operationalizations of Delta for h-m3 Within-Prompt Quality Probe.

Computes Delta = cos(H_next, A_chosen) - cos(H_next, A_rejected) under three
length-control operationalizations:
  OP1 (raw): dot product on L2-normalized embeddings
  OP2 (length_matched): truncate A_chosen to A_rejected token length, re-embed
  OP3 (prompt_projected): project out H_prompt direction, normalize, compute delta

FR-M3 logging format:
  [FR-M3] Tier {tier}: N_pairs={n}, E[Δ_raw]={:.4f}, E[Δ_len]={:.4f}, E[Δ_proj]={:.4f}
"""
import logging
import numpy as np
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

OPERATIONALIZATIONS: List[str] = ["raw", "length_matched", "prompt_projected"]


def truncate_to_rejected_length(
    a_chosen_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
) -> List[str]:
    """Truncate A_chosen whitespace-tokens to len(A_rejected). Returns List[str].

    Edge cases:
    - Empty string: returns empty string
    - Chosen shorter than rejected: no-op (return as-is)
    - Single-token strings: handled naturally

    Args:
        a_chosen_texts: List of A_chosen strings.
        a_chosen_token_lens: Whitespace token counts for A_chosen.
        a_rejected_token_lens: Whitespace token counts for A_rejected.

    Returns:
        List of truncated A_chosen strings.
    """
    result = []
    for text, chosen_len, rejected_len in zip(
        a_chosen_texts, a_chosen_token_lens, a_rejected_token_lens
    ):
        if not text:
            result.append("")
            continue
        if chosen_len <= rejected_len:
            # No-op: chosen is already shorter or equal
            result.append(text)
        else:
            tokens = text.split()
            truncated = " ".join(tokens[:rejected_len])
            result.append(truncated)
    return result


def project_out(
    vecs: np.ndarray,       # [N, D] L2-normalized
    direction: np.ndarray,  # [N, D] L2-normalized per-pair directions
) -> np.ndarray:            # [N, D] projected (NOT re-normalized)
    """Per-pair projection: v - (v·d)*d.

    Vectorized with keepdims for per-pair computation.
    NOTE: Result is NOT re-normalized here; caller handles normalization.

    Args:
        vecs: [N, D] L2-normalized embeddings.
        direction: [N, D] L2-normalized per-pair direction vectors.

    Returns:
        [N, D] projected vectors (H_prompt direction removed).
    """
    proj_coeff = np.sum(vecs * direction, axis=1, keepdims=True)  # [N, 1]
    return vecs - proj_coeff * direction                            # [N, D]


def compute_delta_raw(
    emb_h_next: np.ndarray,     # [N, D]
    emb_a_chosen: np.ndarray,   # [N, D]
    emb_a_rejected: np.ndarray, # [N, D]
) -> np.ndarray:                # [N,]
    """OP1: dot(H_next, A_chosen) - dot(H_next, A_rejected).

    All inputs expected to be L2-normalized (float32).
    Computes elementwise dot product (cosine similarity on normalized vecs).

    Args:
        emb_h_next: [N, D] L2-normalized human follow-up embeddings.
        emb_a_chosen: [N, D] L2-normalized chosen AI response embeddings.
        emb_a_rejected: [N, D] L2-normalized rejected AI response embeddings.

    Returns:
        [N,] float32 array of per-pair delta values.
    """
    cos_chosen = np.sum(emb_h_next * emb_a_chosen, axis=1)    # [N,]
    cos_rejected = np.sum(emb_h_next * emb_a_rejected, axis=1) # [N,]
    return (cos_chosen - cos_rejected).astype(np.float32)       # [N,]


def compute_delta_length_matched(
    h_next_texts: List[str],           # Not directly used (embedder handles encoding)
    a_chosen_texts: List[str],
    a_rejected_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
    embedder,                          # Embedder instance with encode_tier()
    tier: str,
) -> np.ndarray:                       # [N,]
    """OP2: Truncate A_chosen, re-embed, compute delta as OP1.

    Truncates A_chosen to the token length of A_rejected before re-embedding,
    controlling for response length effects.

    Args:
        h_next_texts: Not used (embeddings come from compute_all_deltas context).
        a_chosen_texts: Original A_chosen texts.
        a_rejected_texts: A_rejected texts (for length reference).
        a_chosen_token_lens: Whitespace token counts of A_chosen.
        a_rejected_token_lens: Whitespace token counts of A_rejected.
        embedder: Embedder instance.
        tier: Tier name for cache key construction.

    Returns:
        [N,] float32 delta array.
    """
    truncated = truncate_to_rejected_length(
        a_chosen_texts, a_chosen_token_lens, a_rejected_token_lens
    )
    n_pairs = len(truncated)

    emb_truncated = embedder.encode_tier(
        truncated, prefix="a_chosen_trunc", tier=tier, n_pairs=n_pairs
    )
    emb_h_next = embedder.encode_tier(
        h_next_texts, prefix="h_next_cr", tier=tier, n_pairs=n_pairs
    )
    emb_a_rejected = embedder.encode_tier(
        a_rejected_texts, prefix="a_rejected", tier=tier, n_pairs=n_pairs
    )

    return compute_delta_raw(emb_h_next, emb_truncated, emb_a_rejected)


def compute_delta_prompt_projected(
    emb_h_next: np.ndarray,     # [N, D]
    emb_a_chosen: np.ndarray,   # [N, D]
    emb_a_rejected: np.ndarray, # [N, D]
    emb_h_prompt: np.ndarray,   # [N, D] L2-normalized prompt embeddings
) -> np.ndarray:                # [N,]
    """OP3: Project out H_prompt direction, normalize with 1e-8 guard, compute delta.

    Controls for topic/prompt direction shared between A_chosen and A_rejected.
    Uses per-pair projection (not global direction).

    Args:
        emb_h_next: [N, D] L2-normalized human follow-up embeddings.
        emb_a_chosen: [N, D] L2-normalized chosen AI response embeddings.
        emb_a_rejected: [N, D] L2-normalized rejected AI response embeddings.
        emb_h_prompt: [N, D] L2-normalized prompt context embeddings.

    Returns:
        [N,] float32 delta array after prompt projection.
    """
    # Project out H_prompt direction (per-pair)
    a_chosen_proj = project_out(emb_a_chosen, emb_h_prompt)    # [N, D]
    a_rejected_proj = project_out(emb_a_rejected, emb_h_prompt) # [N, D]

    # Normalize projected embeddings with 1e-8 guard
    a_chosen_norm = np.linalg.norm(a_chosen_proj, axis=1, keepdims=True) + 1e-8  # [N, 1]
    a_rejected_norm = np.linalg.norm(a_rejected_proj, axis=1, keepdims=True) + 1e-8

    a_chosen_proj_normalized = a_chosen_proj / a_chosen_norm    # [N, D]
    a_rejected_proj_normalized = a_rejected_proj / a_rejected_norm

    return compute_delta_raw(emb_h_next, a_chosen_proj_normalized, a_rejected_proj_normalized)


def compute_all_deltas(
    tier_pairs: Dict,  # {h_next, a_chosen, a_rejected, h_prompt, a_chosen_token_len, a_rejected_token_len, n_pairs}
    embedder,          # Embedder instance
    tier: str,
) -> Dict[str, np.ndarray]:
    """Compute all 3 Δ operationalizations for one tier + model.

    Encodes all required embeddings, computes OP1/OP2/OP3, and logs FR-M3 message.

    Args:
        tier_pairs: Dict with h_next, a_chosen, a_rejected, h_prompt text lists
                    plus a_chosen_token_len, a_rejected_token_len, n_pairs.
        embedder: Embedder instance with encode_tier() method.
        tier: Tier name (e.g., 'helpful-base') for cache keys.

    Returns:
        {"raw": [N,], "length_matched": [N,], "prompt_projected": [N,]}
    """
    h_next_texts = tier_pairs["h_next"]
    a_chosen_texts = tier_pairs["a_chosen"]
    a_rejected_texts = tier_pairs["a_rejected"]
    h_prompt_texts = tier_pairs["h_prompt"]
    a_chosen_token_lens = tier_pairs["a_chosen_token_len"]
    a_rejected_token_lens = tier_pairs["a_rejected_token_len"]
    n_pairs = tier_pairs["n_pairs"]

    # Encode all embeddings needed for OP1 and OP3
    emb_h_next = embedder.encode_tier(h_next_texts, prefix="h_next_cr", tier=tier, n_pairs=n_pairs)
    emb_a_chosen = embedder.encode_tier(a_chosen_texts, prefix="a_chosen", tier=tier, n_pairs=n_pairs)
    emb_a_rejected = embedder.encode_tier(a_rejected_texts, prefix="a_rejected", tier=tier, n_pairs=n_pairs)
    emb_h_prompt = embedder.encode_tier(h_prompt_texts, prefix="h_prompt", tier=tier, n_pairs=n_pairs)

    # OP1: raw delta
    delta_raw = compute_delta_raw(emb_h_next, emb_a_chosen, emb_a_rejected)

    # OP2: length-matched delta (re-encodes truncated a_chosen)
    delta_length_matched = compute_delta_length_matched(
        h_next_texts=h_next_texts,
        a_chosen_texts=a_chosen_texts,
        a_rejected_texts=a_rejected_texts,
        a_chosen_token_lens=a_chosen_token_lens,
        a_rejected_token_lens=a_rejected_token_lens,
        embedder=embedder,
        tier=tier,
    )

    # OP3: prompt-projected delta
    delta_prompt_projected = compute_delta_prompt_projected(
        emb_h_next=emb_h_next,
        emb_a_chosen=emb_a_chosen,
        emb_a_rejected=emb_a_rejected,
        emb_h_prompt=emb_h_prompt,
    )

    # FR-M3 logging
    logger.info(
        f"[FR-M3] Tier {tier}: N_pairs={n_pairs}, "
        f"E[Δ_raw]={float(np.mean(delta_raw)):.4f}, "
        f"E[Δ_len]={float(np.mean(delta_length_matched)):.4f}, "
        f"E[Δ_proj]={float(np.mean(delta_prompt_projected)):.4f}"
    )

    return {
        "raw": delta_raw,
        "length_matched": delta_length_matched,
        "prompt_projected": delta_prompt_projected,
    }
