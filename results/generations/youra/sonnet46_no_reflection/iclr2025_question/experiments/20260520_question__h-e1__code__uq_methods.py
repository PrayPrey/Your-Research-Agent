import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

from generate import GenerationResult

logger = logging.getLogger(__name__)


def _get_entailment_prob(
    text_a: str,
    text_b: str,
    nli_model: Any,
    nli_tokenizer: Any,
) -> float:
    """Return entailment probability P(a entails b) from DeBERTa NLI model."""
    inputs = nli_tokenizer(
        text_a, text_b, return_tensors="pt", truncation=True, max_length=512
    )
    device = next(nli_model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = nli_model(**inputs).logits[0]  # [3]: contradiction, neutral, entailment
    probs = torch.softmax(logits, dim=-1)
    return probs[2].item()  # entailment index


def compute_token_probability(result: GenerationResult) -> float:
    """Negative log-likelihood of greedy decode. Higher = more uncertain."""
    return -result.greedy_log_likelihood


def compute_semantic_entropy(
    result: GenerationResult,
    nli_model: Any,
    nli_tokenizer: Any,
    entailment_threshold: float = 0.5,
) -> Tuple[float, int]:
    """NLI-based semantic clustering + entropy. Returns (se_score, K)."""
    texts = result.sampled_texts
    N = len(texts)
    if N == 0:
        return 0.0, 0

    # Build NxN entailment matrix
    entail_prob = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for j in range(N):
            if i != j and texts[i] and texts[j]:
                entail_prob[i, j] = _get_entailment_prob(
                    texts[i], texts[j], nli_model, nli_tokenizer
                )

    # Assign clusters via bidirectional entailment
    cluster_id = [-1] * N
    next_id = 0
    for i in range(N):
        if cluster_id[i] == -1:
            cluster_id[i] = next_id
            next_id += 1
        for j in range(i + 1, N):
            if cluster_id[j] == -1:
                if (
                    entail_prob[i, j] > entailment_threshold
                    and entail_prob[j, i] > entailment_threshold
                ):
                    cluster_id[j] = cluster_id[i]

    # Compute cluster probabilities
    unique_clusters = list(set(cluster_id))
    K = len(unique_clusters)
    cluster_probs = np.array(
        [cluster_id.count(c) / N for c in unique_clusters], dtype=np.float64
    )

    # Shannon entropy
    se_score = -np.sum(cluster_probs * np.log(cluster_probs + 1e-10))
    return float(se_score), K


def compute_kle(
    result: GenerationResult,
    nli_model: Any,
    nli_tokenizer: Any,
) -> Optional[float]:
    """EigValLaplacian via lm-polygraph; returns None if unavailable."""
    try:
        from lm_polygraph.estimators import EigValLaplacian  # noqa: F401
    except ImportError:
        logger.debug("lm-polygraph not available; computing KLE manually")

    texts = result.sampled_texts
    N = len(texts)
    if N == 0:
        return None

    # Build NxN entailment matrix
    A = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for j in range(N):
            if i != j and texts[i] and texts[j]:
                A[i, j] = _get_entailment_prob(
                    texts[i], texts[j], nli_model, nli_tokenizer
                )

    # Graph Laplacian L = D - A
    D = np.diag(A.sum(axis=1))
    L = D - A

    # Sum of positive eigenvalues
    eigvals = np.linalg.eigvalsh(L)
    kle_score = float(np.sum(np.maximum(eigvals, 0)))
    return kle_score


def compute_selfcheck_bertscore(result: GenerationResult) -> float:
    """BERTScore consistency of samples vs greedy. Higher = more uncertain."""
    try:
        from bert_score import score as bert_score_fn

        refs = [result.greedy_text] * len(result.sampled_texts)
        cands = result.sampled_texts
        if not cands or not any(cands):
            return 0.0
        _, _, F = bert_score_fn(cands, refs, lang="en", verbose=False)
        mean_f1 = F.mean().item()
        return 1.0 - mean_f1  # higher inconsistency = higher uncertainty
    except ImportError:
        logger.debug("bert_score not available; returning 0")
        return 0.0


def compute_selfcheck_nli(
    result: GenerationResult,
    nli_model: Any,
    nli_tokenizer: Any,
) -> float:
    """NLI contradiction of samples vs greedy. Higher = more uncertain."""
    if not result.sampled_texts or not result.greedy_text:
        return 0.0
    contradiction_probs = []
    for text in result.sampled_texts:
        if not text:
            continue
        inputs = nli_tokenizer(
            result.greedy_text, text, return_tensors="pt", truncation=True, max_length=512
        )
        device = next(nli_model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = nli_model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1)
        contradiction_probs.append(probs[0].item())  # contradiction class
    return float(np.mean(contradiction_probs)) if contradiction_probs else 0.0


def compute_seps(
    result: GenerationResult,
    probe_model: Optional[Any] = None,
) -> Optional[float]:
    """Linear probe on hidden states. Returns None if probe_model or hidden states unavailable."""
    if probe_model is None or result.hidden_states_last is None:
        return None
    try:
        hs = result.hidden_states_last  # [n_layers, hidden_dim] (last token)
        # Flatten last layer hidden state as feature
        feat = hs[-1].reshape(1, -1)
        score = probe_model.predict_proba(feat)[0][0]  # P(incorrect)
        return float(score)
    except Exception as e:
        logger.debug(f"SEPs computation failed: {e}")
        return None


def compute_all_uq(
    results: List[GenerationResult],
    nli_model: Any,
    nli_tokenizer: Any,
) -> Tuple[Dict[str, np.ndarray], List[int]]:
    """Compute all UQ methods for list of GenerationResults.

    Returns:
        uq_scores: dict method_name -> [Q] float array
        cluster_counts: list of K values from semantic entropy
    """
    Q = len(results)
    token_probs = np.zeros(Q)
    se_scores = np.zeros(Q)
    kle_scores = np.full(Q, np.nan)
    sc_bert_scores = np.zeros(Q)
    sc_nli_scores = np.zeros(Q)
    seps_scores = np.full(Q, np.nan)
    cluster_counts = []

    for i, result in enumerate(results):
        token_probs[i] = compute_token_probability(result)
        se, K = compute_semantic_entropy(result, nli_model, nli_tokenizer)
        se_scores[i] = se
        cluster_counts.append(K)

        kle = compute_kle(result, nli_model, nli_tokenizer)
        if kle is not None:
            kle_scores[i] = kle

        sc_bert_scores[i] = compute_selfcheck_bertscore(result)
        sc_nli_scores[i] = compute_selfcheck_nli(result, nli_model, nli_tokenizer)

        if (i + 1) % 100 == 0:
            logger.info(f"UQ computed for {i + 1}/{Q} queries")

    uq_scores = {
        "token_prob": token_probs,
        "semantic_entropy": se_scores,
        "kle": kle_scores,
        "selfcheck_bertscore": sc_bert_scores,
        "selfcheck_nli": sc_nli_scores,
        "seps": seps_scores,
    }
    return uq_scores, cluster_counts


def verify_se_mechanism(
    cluster_counts: List[int],
    n_samples: int = 10,
) -> Tuple[bool, Dict[str, Any]]:
    """Check mean cluster count K < N. Returns (ok, stats_dict)."""
    if not cluster_counts:
        return False, {"mean_k": 0, "min_k": 0, "max_k": 0, "degenerate_fraction": 1.0}
    arr = np.array(cluster_counts, dtype=float)
    mean_k = float(arr.mean())
    min_k = int(arr.min())
    max_k = int(arr.max())
    degenerate_fraction = float((arr >= n_samples).mean())
    ok = mean_k < n_samples
    stats = {
        "mean_k": mean_k,
        "min_k": min_k,
        "max_k": max_k,
        "degenerate_fraction": degenerate_fraction,
    }
    if ok:
        logger.info(f"SE mechanism activated: mean K={mean_k:.2f} < N={n_samples}")
    else:
        logger.warning(f"SE degenerate: mean K={mean_k:.2f} >= N={n_samples}")
    return ok, stats
