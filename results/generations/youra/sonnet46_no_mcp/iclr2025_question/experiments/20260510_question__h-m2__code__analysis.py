import numpy as np
from typing import Dict, Any
from scipy.stats import pointbiserialr

from config import ExperimentConfig


def compute_aggregation_rate(cluster_counts: np.ndarray, n_samples: int = 5) -> float:
    """Fraction of examples where cluster_count < n_samples."""
    return float(np.mean(cluster_counts < n_samples))


def compute_collapse_rate(cluster_counts: np.ndarray) -> float:
    """Fraction of examples where cluster_count == 1 (full collapse)."""
    return float(np.mean(cluster_counts == 1))


def compute_distribution_stats(cluster_counts: np.ndarray) -> Dict[str, Any]:
    """Mean, std, median, histogram {1..5} of cluster counts."""
    histogram = {str(k): int(np.sum(cluster_counts == k)) for k in range(1, 6)}
    return {
        "mean_cluster_count": float(np.mean(cluster_counts)),
        "std_cluster_count": float(np.std(cluster_counts)),
        "median_cluster_count": float(np.median(cluster_counts)),
        "histogram": histogram,
    }


def bootstrap_aggregation_ci(
    cluster_counts: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
    n_samples: int = 5,
) -> Dict[str, Any]:
    """Percentile bootstrap 95% CI on aggregation_rate.

    Returns: {aggregation_rate, ci_lower, ci_upper, gate_pass}
    gate_pass = (aggregation_rate >= 0.50) AND (ci_lower >= 0.30)
    """
    N = len(cluster_counts)
    rate_obs = float(np.mean(cluster_counts < n_samples))

    rng = np.random.default_rng(seed)
    boot_rates = np.empty(n_resamples)
    for i in range(n_resamples):
        idx = rng.integers(0, N, size=N)
        boot_rates[i] = np.mean(cluster_counts[idx] < n_samples)

    ci_lower, ci_upper = np.percentile(boot_rates, [2.5, 97.5])
    gate_pass = bool(rate_obs >= 0.50 and ci_lower >= 0.30)

    return {
        "aggregation_rate": rate_obs,
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "gate_pass": gate_pass,
    }


def compute_pointbiserial_correlation(
    labels: np.ndarray,
    cluster_counts: np.ndarray,
) -> Dict[str, Any]:
    """Point-biserial correlation between hallucination labels and cluster counts."""
    r_pb, p_value = pointbiserialr(labels, cluster_counts)
    return {
        "r_pb": float(r_pb),
        "p_value": float(p_value),
        "meaningful": bool(abs(r_pb) >= 0.10),
    }


def stratified_aggregation_by_type(
    cluster_counts: np.ndarray,
    dataset: list,
    n_samples: int = 5,
) -> Dict[str, float] | None:
    """Compute aggregation_rate per question_type if field present."""
    if not dataset or "question_type" not in dataset[0]:
        return None
    type_map: Dict[str, list] = {}
    for i, record in enumerate(dataset):
        qt = record.get("question_type", "unknown")
        type_map.setdefault(qt, []).append(int(cluster_counts[i]))
    return {
        qt: float(np.mean(np.array(counts) < n_samples))
        for qt, counts in type_map.items()
    }


def evaluate_gate(bootstrap_result: Dict[str, Any], cfg: ExperimentConfig) -> str:
    """Return 'PASS', 'PARTIAL', or 'PIVOT' based on aggregation_rate and ci_lower."""
    rate = bootstrap_result["aggregation_rate"]
    ci_lower = bootstrap_result["ci_lower"]

    if rate >= cfg.aggregation_gate_threshold and ci_lower >= cfg.aggregation_ci_lower_threshold:
        return "PASS"
    elif rate >= cfg.aggregation_ci_lower_threshold:
        return "PARTIAL"
    else:
        return "PIVOT"


RESULTS_SCHEMA = {
    "required_keys": [
        "hypothesis_id",
        "cluster_count_source",
        "n_examples",
        "mean_cluster_count",
        "std_cluster_count",
        "median_cluster_count",
        "histogram",
        "aggregation_rate",
        "collapse_rate",
        "bootstrap_ci_lower",
        "bootstrap_ci_upper",
        "gate_pass",
        "gate_result",
        "r_pb",
        "p_value",
        "stratified_aggregation",
        "timestamp",
    ]
}


def validate_results_schema(results: Dict[str, Any]) -> None:
    """Raise KeyError if any required key missing from results."""
    for key in RESULTS_SCHEMA["required_keys"]:
        if key not in results:
            raise KeyError(f"Missing required key in results: '{key}'")
