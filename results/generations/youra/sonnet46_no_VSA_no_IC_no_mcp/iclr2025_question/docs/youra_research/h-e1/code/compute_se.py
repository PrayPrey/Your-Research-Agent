"""Semantic Entropy computation for H-E1 (Kuhn et al. 2023)."""
import numpy as np
from scipy.special import logsumexp
from transformers import pipeline


def load_nli_model(model_id: str = "cross-encoder/nli-deberta-v3-large", device: int = 0):
    """Load NLI pipeline for zero-shot classification on GPU."""
    try:
        nli = pipeline("zero-shot-classification", model=model_id, device=device)
        return nli
    except Exception as e:
        raise RuntimeError(f"Failed to load NLI model {model_id}: {e}")


def _nli_entailment_score(premise: str, hypothesis: str, nli_pipeline) -> float:
    """Get entailment score for a premise->hypothesis pair."""
    result = nli_pipeline(
        premise,
        candidate_labels=[hypothesis],
        hypothesis_template="{}",
    )
    # zero-shot-classification returns scores for the candidate labels
    # But for NLI entailment we use text entailment directly
    # Use NLI pipeline differently: feed as text pair
    return result["scores"][0]


def _batch_nli_entailment(pairs: list, nli_pipeline) -> list:
    """
    Batch NLI entailment check using zero-shot-classification.
    Each pair is (premise, hypothesis); returns list of entailment scores.
    Uses cross-encoder which handles sequence pairs directly.
    """
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    # Access underlying model from pipeline
    model = nli_pipeline.model
    tokenizer = nli_pipeline.tokenizer
    device = next(model.parameters()).device

    entailment_scores = []
    batch_size = 32
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i+batch_size]
        premises = [p for p, h in batch]
        hyps = [h for p, h in batch]
        enc = tokenizer(
            premises, hyps,
            padding=True, truncation=True, max_length=256,
            return_tensors="pt"
        ).to(device)
        with torch.no_grad():
            logits = model(**enc).logits  # (B, num_labels)
        probs = torch.softmax(logits.float(), dim=-1)
        # Standard MNLI label order: contradiction=0, neutral=1, entailment=2
        # cross-encoder/nli-deberta-v3-large: check label mapping
        id2label = model.config.id2label
        entailment_idx = None
        for idx, label in id2label.items():
            if "entail" in label.lower():
                entailment_idx = idx
                break
        if entailment_idx is None:
            entailment_idx = 2  # default MNLI order
        entailment_scores.extend(probs[:, entailment_idx].cpu().tolist())
    return entailment_scores


def get_semantic_ids(strings_list: list, nli_pipeline) -> list:
    """
    Bidirectional NLI entailment clustering (Kuhn et al. 2023).
    Returns cluster id per sample.
    """
    K = len(strings_list)
    cluster_ids = [-1] * K
    next_cluster = 0

    # Build all pairs for batching
    pairs_i = []
    pairs_j = []
    pair_indices = []
    for i in range(K):
        for j in range(i + 1, K):
            pairs_i.append((strings_list[i], strings_list[j]))
            pairs_j.append((strings_list[j], strings_list[i]))
            pair_indices.append((i, j))

    if not pairs_i:
        return list(range(K))

    scores_ij = _batch_nli_entailment(pairs_i, nli_pipeline)
    scores_ji = _batch_nli_entailment(pairs_j, nli_pipeline)

    # Build bidirectional entailment matrix
    entails = {}
    for (i, j), sij, sji in zip(pair_indices, scores_ij, scores_ji):
        entails[(i, j)] = (sij > 0.5 and sji > 0.5)

    # Greedy clustering: assign cluster ids
    for i in range(K):
        if cluster_ids[i] == -1:
            cluster_ids[i] = next_cluster
            next_cluster += 1
        for j in range(i + 1, K):
            if cluster_ids[j] == -1 and entails.get((i, j), False):
                cluster_ids[j] = cluster_ids[i]

    return cluster_ids


def aggregate_log_probs_by_cluster(log_probs: np.ndarray, semantic_ids: list) -> np.ndarray:
    """logsumexp aggregation per cluster. Returns (n_clusters,) array."""
    unique_clusters = sorted(set(semantic_ids))
    cluster_log_probs = []
    for c in unique_clusters:
        indices = [i for i, sid in enumerate(semantic_ids) if sid == c]
        cluster_lp = logsumexp(log_probs[indices])
        cluster_log_probs.append(cluster_lp)
    return np.array(cluster_log_probs)


def compute_se_scores(questions: list, samples_map: dict, nli_pipeline) -> tuple:
    """
    Full SE pipeline. Returns (se_scores: list[float], avg_clusters: float).
    """
    se_scores = []
    cluster_counts = []

    for i, q in enumerate(questions):
        qid = q["question_id"]
        sdata = samples_map.get(qid, {})
        samples = sdata.get("samples", [])
        log_probs = sdata.get("log_probs", [])

        if len(samples) < 2 or len(log_probs) < 2:
            # fallback: single cluster = max entropy = log(1) = 0
            se_scores.append(0.0)
            cluster_counts.append(1)
            continue

        # Truncate to min of samples and log_probs
        K = min(len(samples), len(log_probs))
        samples = samples[:K]
        log_probs_arr = np.array(log_probs[:K], dtype=np.float64)

        semantic_ids = get_semantic_ids(samples, nli_pipeline)
        cluster_lp = aggregate_log_probs_by_cluster(log_probs_arr, semantic_ids)

        # Normalize
        cluster_lp = cluster_lp - logsumexp(cluster_lp)
        probs = np.exp(cluster_lp)
        se = -np.sum(probs * np.log(probs + 1e-9))
        se_scores.append(float(se))
        cluster_counts.append(len(set(semantic_ids)))

        if (i + 1) % 10 == 0:
            print(f"  SE: {i+1}/{len(questions)} done, avg_clusters_so_far={np.mean(cluster_counts):.2f}")

    return se_scores, float(np.mean(cluster_counts))
