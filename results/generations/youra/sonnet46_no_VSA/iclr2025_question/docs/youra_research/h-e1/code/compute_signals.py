"""SE_N5 and min_logprob signal computation."""
import numpy as np
from tqdm import tqdm
from sentence_transformers import CrossEncoder

from config import NLI_ID, N_PROMPTS


def load_nli_model(model_id: str = NLI_ID):
    """Load sentence_transformers CrossEncoder for NLI."""
    return CrossEncoder(model_id)


def check_implication(text1: str, text2: str, nli_model) -> int:
    """Returns 0=contradiction, 1=neutral, 2=entailment."""
    score = nli_model.predict([(text1, text2)])
    return int(np.argmax(score[0]))


def get_semantic_ids(responses: list[str], nli_model) -> list[int]:
    """Bidirectional NLI clustering, non-strict equivalence.
    Non-strict: equivalent if no contradiction AND not both neutral.
    Adapted from jlko/semantic_uncertainty.
    """
    n = len(responses)
    semantic_ids = list(range(n))

    for i in range(n):
        for j in range(i + 1, n):
            imp_ij = check_implication(responses[i], responses[j], nli_model)
            imp_ji = check_implication(responses[j], responses[i], nli_model)
            no_contradiction = (imp_ij != 0) and (imp_ji != 0)
            not_both_neutral = not (imp_ij == 1 and imp_ji == 1)
            if no_contradiction and not_both_neutral:
                old_id = semantic_ids[j]
                new_id = semantic_ids[i]
                semantic_ids = [new_id if s == old_id else s for s in semantic_ids]

    # Remap to contiguous 0..K-1
    unique = sorted(set(semantic_ids))
    remap = {v: k for k, v in enumerate(unique)}
    return [remap[s] for s in semantic_ids]


def cluster_assignment_entropy(semantic_ids: list[int]) -> float:
    """SE = -sum(p_k * log(p_k)). Returns 0.0 for single cluster."""
    counts = np.bincount(semantic_ids)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log(probs + 1e-10)))


def compute_se_n5(
    stochastic_responses: list[list[str]],
    nli_model,
    batch_nli_size: int = 50,
) -> np.ndarray:
    """Compute SE_N5 for all prompts. Asserts var > 0.01. Returns shape (N_PROMPTS,)."""
    se_scores = []
    for i in tqdm(range(len(stochastic_responses)), desc="Computing SE_N5"):
        responses = stochastic_responses[i]
        ids = get_semantic_ids(responses, nli_model)
        se_scores.append(cluster_assignment_entropy(ids))
    se = np.array(se_scores)
    assert np.var(se) > 0.01, f"SE degenerate: var={np.var(se):.4f}"
    return se


def compute_min_logprob(
    token_logprobs_per_prompt: list[list[float]],
) -> np.ndarray:
    """Min token log-prob per prompt. Asserts all values < 0. Returns shape (N_PROMPTS,)."""
    min_lp = np.array([min(lp) for lp in token_logprobs_per_prompt])
    assert np.all(min_lp < 0), (
        f"Expected all log-probs < 0; got {(min_lp >= 0).sum()} non-negative values"
    )
    return min_lp


def compute_response_lengths(greedy_answers: list[str]) -> np.ndarray:
    """Token count approximation (whitespace split). Returns shape (N_PROMPTS,)."""
    return np.array([len(ans.split()) for ans in greedy_answers])


def verify_signals(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
) -> None:
    """Assert signal properties. Raises AssertionError on failure."""
    assert np.var(se_scores) > 0.01, f"SE degenerate: var={np.var(se_scores):.4f}"
    assert np.all(min_logprob_scores < 0), "min_logprob has non-negative values"
    assert len(se_scores) == N_PROMPTS, f"Expected {N_PROMPTS} SE scores, got {len(se_scores)}"
    assert len(min_logprob_scores) == N_PROMPTS, (
        f"Expected {N_PROMPTS} min_logprob scores, got {len(min_logprob_scores)}"
    )
    print(
        f"✓ Signals verified: SE var={np.var(se_scores):.4f}, "
        f"min_logprob mean={np.mean(min_logprob_scores):.4f}, "
        f"n={len(se_scores)}"
    )
