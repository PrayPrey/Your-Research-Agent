"""Distribution overlap analysis for H-M1 reward conflation hypothesis."""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from data import Task


def distribution_overlap(dist_a: np.ndarray, dist_b: np.ndarray, bins: int = 50) -> float:
    """Compute histogram intersection overlap between two distributions."""
    if len(dist_a) == 0 or len(dist_b) == 0:
        return float("nan")

    # Combine to get common range
    all_vals = np.concatenate([dist_a, dist_b])
    min_val, max_val = all_vals.min(), all_vals.max()

    if min_val == max_val:
        return 1.0  # All same value = perfect overlap

    hist_a, edges = np.histogram(dist_a, bins=bins, range=(min_val, max_val), density=True)
    hist_b, _ = np.histogram(dist_b, bins=edges, density=True)

    bin_width = edges[1] - edges[0]
    overlap = np.sum(np.minimum(hist_a, hist_b)) * bin_width
    return float(overlap)


def mean_confidence_diff(dist_a: np.ndarray, dist_b: np.ndarray) -> float:
    """Compute absolute difference in means."""
    if len(dist_a) == 0 or len(dist_b) == 0:
        return float("nan")
    return abs(np.mean(dist_a) - np.mean(dist_b))


def cluster_task_correlation(
    cluster_labels: List[int], task_types: List[str]
) -> Tuple[float, float]:
    """Point-biserial correlation between cluster assignment and task type."""
    # Convert task_types to binary: A=0, B=1
    type_binary = np.array([1 if t == "B" else 0 for t in task_types])
    cluster_array = np.array(cluster_labels)

    if len(np.unique(type_binary)) < 2 or len(np.unique(cluster_array)) < 2:
        return (0.0, 1.0)  # No variance

    r, p = stats.pointbiserialr(cluster_array, type_binary)
    return (float(r), float(p))


def analyze_conflation(
    confidences: Dict[str, float],
    task_types: Dict[str, str],
    overlap_gate: float = 0.7,
    mean_diff_gate: float = 0.1,
    overlap_fail_gate: float = 0.5,
    mean_diff_fail_gate: float = 0.2,
    bins: int = 50,
) -> Dict:
    """Full conflation analysis with gate logic."""
    dist_a = np.array([confidences[tid] for tid in confidences if task_types.get(tid) == "A"])
    dist_b = np.array([confidences[tid] for tid in confidences if task_types.get(tid) == "B"])

    overlap = distribution_overlap(dist_a, dist_b, bins)
    diff = mean_confidence_diff(dist_a, dist_b)

    gate_pass = (overlap > overlap_gate) or (diff < mean_diff_gate)
    gate_fail = (overlap < overlap_fail_gate) and (diff > mean_diff_fail_gate)

    return {
        "mean_a": float(np.mean(dist_a)) if len(dist_a) > 0 else None,
        "mean_b": float(np.mean(dist_b)) if len(dist_b) > 0 else None,
        "std_a": float(np.std(dist_a)) if len(dist_a) > 0 else None,
        "std_b": float(np.std(dist_b)) if len(dist_b) > 0 else None,
        "n_a": len(dist_a),
        "n_b": len(dist_b),
        "diff": float(diff),
        "overlap": float(overlap),
        "gate_pass": bool(gate_pass),
        "gate_fail": bool(gate_fail),
        "dist_a": dist_a.tolist(),
        "dist_b": dist_b.tolist(),
    }


def cross_model_overlap(
    conf_by_model: Dict[str, Dict[str, float]],
    task_types: Dict[str, str],
    bins: int = 50,
) -> Dict[str, float]:
    """Compute overlap for each model."""
    result = {}
    for model_id, conf in conf_by_model.items():
        dist_a = np.array([conf[tid] for tid in conf if task_types.get(tid) == "A"])
        dist_b = np.array([conf[tid] for tid in conf if task_types.get(tid) == "B"])
        result[model_id] = distribution_overlap(dist_a, dist_b, bins)
    return result


def per_dataset_overlap(
    tasks: List[Task],
    confidences: Dict[str, float],
    task_types: Dict[str, str],
    bins: int = 50,
) -> Dict[str, float]:
    """Compute overlap per dataset (ABL-3)."""
    datasets = {"truthfulqa", "mmlu_moral", "anthropic_hh"}
    result = {}

    for ds in datasets:
        ids = [t["task_id"] for t in tasks if t["source_dataset"] == ds]
        dist_a = np.array([confidences[i] for i in ids if task_types.get(i) == "A" and i in confidences])
        dist_b = np.array([confidences[i] for i in ids if task_types.get(i) == "B" and i in confidences])

        if len(dist_a) >= 2 and len(dist_b) >= 2:
            result[ds] = distribution_overlap(dist_a, dist_b, bins)
        else:
            result[ds] = float("nan")

    return result
