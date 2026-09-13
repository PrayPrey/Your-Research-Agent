"""
Evaluation utilities for EmbedPrint data attribution.
"""
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_precision_at_k(
    predicted_clusters: np.ndarray,
    true_clusters: np.ndarray,
    k: int,
) -> float:
    """
    Compute precision@k for cluster attribution.

    Args:
        predicted_clusters: Predicted cluster rankings [num_queries, num_clusters]
        true_clusters: True cluster IDs [num_queries]
        k: Top-k value

    Returns:
        Precision@k score
    """
    num_queries = len(true_clusters)
    correct = 0

    for i in range(num_queries):
        top_k_pred = np.argsort(predicted_clusters[i])[-k:][::-1]
        if true_clusters[i] in top_k_pred:
            correct += 1

    return correct / num_queries


def compute_recall_at_k(
    predicted_clusters: np.ndarray,
    true_clusters: np.ndarray,
    k: int,
) -> float:
    """
    Compute recall@k for cluster attribution.
    (For single ground-truth, this equals precision@k)
    """
    return compute_precision_at_k(predicted_clusters, true_clusters, k)


def compute_mrr(
    predicted_clusters: np.ndarray,
    true_clusters: np.ndarray,
) -> float:
    """
    Compute Mean Reciprocal Rank.

    Args:
        predicted_clusters: Predicted cluster scores [num_queries, num_clusters]
        true_clusters: True cluster IDs [num_queries]

    Returns:
        MRR score
    """
    num_queries = len(true_clusters)
    rr_sum = 0.0

    for i in range(num_queries):
        ranked = np.argsort(predicted_clusters[i])[::-1]
        rank = np.where(ranked == true_clusters[i])[0]
        if len(rank) > 0:
            rr_sum += 1.0 / (rank[0] + 1)

    return rr_sum / num_queries


def evaluate_embedprint_attribution(
    model,
    train_texts: List[str],
    test_texts: List[str],
    train_cluster_ids: np.ndarray,
    test_cluster_ids: np.ndarray,
    tokenizer,
    config,
    device: str = "cuda",
) -> Dict[str, float]:
    """
    Evaluate EmbedPrint attribution performance.

    Returns:
        Dictionary with precision@k, recall@k, MRR, and latency metrics
    """
    model.eval()
    results = {}

    # Get attribution scores for test samples
    all_scores = []
    latencies = []

    for text in tqdm(test_texts, desc="EmbedPrint Attribution"):
        encoding = tokenizer(
            text,
            max_length=config.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)

        start_time = time.time()
        with torch.no_grad():
            outputs = model(input_ids, attention_mask, return_attribution=True)
            scores = outputs["attribution_scores"][0].cpu().numpy()
        latency = (time.time() - start_time) * 1000  # ms

        all_scores.append(scores)
        latencies.append(latency)

    all_scores = np.array(all_scores)

    # Compute metrics
    for k in config.top_k_values:
        results[f"precision@{k}"] = compute_precision_at_k(all_scores, test_cluster_ids, k)
        results[f"recall@{k}"] = compute_recall_at_k(all_scores, test_cluster_ids, k)

    results["mrr"] = compute_mrr(all_scores, test_cluster_ids)
    results["avg_latency_ms"] = np.mean(latencies)
    results["std_latency_ms"] = np.std(latencies)
    results["throughput_qps"] = 1000 / np.mean(latencies)

    return results


def evaluate_baseline_attribution(
    attributor,
    train_texts: List[str],
    test_texts: List[str],
    train_cluster_ids: np.ndarray,
    test_cluster_ids: np.ndarray,
    num_clusters: int,
    method_name: str = "Baseline",
) -> Dict[str, float]:
    """
    Evaluate baseline attribution methods.
    """
    results = {}
    latencies = []

    # Get cluster-level attribution scores
    start_time = time.time()
    if hasattr(attributor, "get_cluster_attribution"):
        all_scores = attributor.get_cluster_attribution(test_texts, num_clusters)
    else:
        # For methods that return sample-level scores
        sample_scores = attributor.compute_attribution(test_texts)
        # Aggregate to cluster level
        all_scores = np.zeros((len(test_texts), num_clusters))
        for i in range(num_clusters):
            mask = train_cluster_ids == i
            if mask.sum() > 0:
                all_scores[:, i] = sample_scores[:, mask].mean(axis=1)

    total_time = time.time() - start_time
    avg_latency = (total_time / len(test_texts)) * 1000  # ms per query

    # Compute metrics
    for k in [1, 5, 10, 20]:
        results[f"precision@{k}"] = compute_precision_at_k(all_scores, test_cluster_ids, k)
        results[f"recall@{k}"] = compute_recall_at_k(all_scores, test_cluster_ids, k)

    results["mrr"] = compute_mrr(all_scores, test_cluster_ids)
    results["avg_latency_ms"] = avg_latency
    results["throughput_qps"] = 1000 / avg_latency if avg_latency > 0 else 0

    logger.info(f"{method_name}: P@10={results['precision@10']:.3f}, MRR={results['mrr']:.3f}, Latency={avg_latency:.2f}ms")

    return results


def evaluate_gradient_attribution(
    attributor,
    model,
    train_loader,
    test_texts: List[str],
    test_cluster_ids: np.ndarray,
    train_cluster_ids: np.ndarray,
    tokenizer,
    config,
    num_samples: int = 100,
    method_name: str = "Gradient",
    device: str = "cuda",
) -> Dict[str, float]:
    """
    Evaluate gradient-based attribution methods (TracIn, Influence Functions).
    """
    results = {}
    num_clusters = config.total_clusters

    all_scores = []
    latencies = []

    for text, true_cluster in tqdm(
        zip(test_texts[:20], test_cluster_ids[:20]),  # Limit for efficiency
        desc=f"{method_name} Attribution",
        total=min(20, len(test_texts)),
    ):
        encoding = tokenizer(
            text,
            max_length=config.max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        query_ids = encoding["input_ids"].to(device)
        query_mask = encoding["attention_mask"].to(device)

        start_time = time.time()
        sample_scores = attributor.compute_attribution(query_ids, query_mask, train_loader, num_samples)
        latency = (time.time() - start_time) * 1000

        # Aggregate to cluster level
        cluster_scores = np.zeros(num_clusters)
        for i in range(min(len(sample_scores), len(train_cluster_ids))):
            cluster_id = train_cluster_ids[i]
            if cluster_id < num_clusters:
                cluster_scores[cluster_id] += sample_scores[i]

        all_scores.append(cluster_scores)
        latencies.append(latency)

    all_scores = np.array(all_scores)
    test_cluster_subset = test_cluster_ids[:len(all_scores)]

    # Compute metrics
    for k in [1, 5, 10, 20]:
        results[f"precision@{k}"] = compute_precision_at_k(all_scores, test_cluster_subset, k)

    results["mrr"] = compute_mrr(all_scores, test_cluster_subset)
    results["avg_latency_ms"] = np.mean(latencies)
    results["throughput_qps"] = 1000 / np.mean(latencies) if np.mean(latencies) > 0 else 0

    logger.info(f"{method_name}: P@10={results['precision@10']:.3f}, MRR={results['mrr']:.3f}, Latency={np.mean(latencies):.2f}ms")

    return results


def compute_loo_correlation(
    attribution_scores: np.ndarray,
    loo_effects: np.ndarray,
) -> float:
    """
    Compute correlation between attribution scores and leave-one-out effects.
    """
    if len(attribution_scores) != len(loo_effects):
        min_len = min(len(attribution_scores), len(loo_effects))
        attribution_scores = attribution_scores[:min_len]
        loo_effects = loo_effects[:min_len]

    correlation = np.corrcoef(attribution_scores, loo_effects)[0, 1]
    return correlation if not np.isnan(correlation) else 0.0


def evaluate_model_quality(
    model,
    eval_loader,
    device: str = "cuda",
) -> Dict[str, float]:
    """
    Evaluate language model quality metrics.
    """
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for batch in tqdm(eval_loader, desc="Evaluating LM Quality"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)

            if hasattr(outputs, "lm_loss"):
                loss = outputs["lm_loss"]
            else:
                logits = outputs.logits
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = input_ids[..., 1:].contiguous()
                loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100,
                    reduction="sum",
                )
                total_tokens += (shift_labels != -100).sum().item()
                total_loss += loss.item()
                continue

            total_loss += loss.item() * input_ids.size(0)
            total_tokens += attention_mask.sum().item()

    avg_loss = total_loss / max(total_tokens, 1)
    perplexity = np.exp(min(avg_loss, 100))  # Cap to avoid overflow

    return {
        "eval_loss": avg_loss,
        "perplexity": perplexity,
    }
