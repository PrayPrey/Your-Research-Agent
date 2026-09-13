# evaluate.py - AUROC computation and mechanism verification
import numpy as np
from sklearn.metrics import roc_auc_score
from config import AUROC_GATE, NUM_SAMPLES


def compute_auroc(y_true: list[int], scores: list[float]) -> float:
    """AUROC with fallback for single-class labels."""
    if len(set(y_true)) < 2:
        return 0.5
    return roc_auc_score(y_true, scores)


def verify_mechanism(results: list[dict]) -> dict:
    """Check: avg_clusters < num_samples, entropy std > 0, cluster sizes vary."""
    avg_clusters = np.mean([r["num_clusters"] for r in results])
    entropies = [r["semantic_entropy"] for r in results]
    entropy_std = np.std(entropies)
    all_sizes = [s for r in results for s in r["cluster_sizes"]]
    cluster_variety = len(set(all_sizes)) > 1
    passed = (avg_clusters < NUM_SAMPLES) and (entropy_std > 0) and cluster_variety
    return {
        "avg_clusters": float(avg_clusters),
        "entropy_std": float(entropy_std),
        "cluster_size_variety": cluster_variety,
        "passed": passed
    }


def apply_gate(semantic_auroc: float, threshold: float = AUROC_GATE) -> dict:
    """Apply MUST_WORK gate: AUROC >= 0.70."""
    passed = semantic_auroc >= threshold
    return {
        "gate": "PASSED" if passed else "FAILED",
        "auroc": semantic_auroc,
        "threshold": threshold,
        "result": f"Semantic entropy AUROC={semantic_auroc:.4f} {'≥' if passed else '<'} {threshold}"
    }
