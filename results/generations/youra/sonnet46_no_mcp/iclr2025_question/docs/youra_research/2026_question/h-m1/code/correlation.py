import json
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any, List


def load_uq_scores(te_path: str, se_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load token_entropy_mean.json and semantic_entropy.json. Returns arrays shape (2000,)."""
    with open(te_path, "r") as f:
        te_dict = json.load(f)
    with open(se_path, "r") as f:
        se_dict = json.load(f)

    common_ids = sorted(set(te_dict.keys()) & set(se_dict.keys()), key=lambda x: int(x))
    assert len(common_ids) == 2000, f"Expected 2000 common IDs, got {len(common_ids)}"

    te = np.array([te_dict[k] for k in common_ids], dtype=float)
    se = np.array([se_dict[k] for k in common_ids], dtype=float)
    return te, se


def check_degenerate(se: np.ndarray, threshold: float = 1e-6) -> bool:
    """Return True if std(se) < threshold (constant semantic entropy)."""
    return float(np.std(se)) < threshold


def inspect_cluster_distribution(samples_path: str) -> Dict[str, Any]:
    """
    Load stochastic_samples.jsonl and compute cluster count distribution
    as a proxy for degenerate SE diagnosis.
    Returns: {cluster_counts, mean_clusters, std_clusters, histogram}
    """
    cluster_counts = []
    with open(samples_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            samples = record.get("samples", [])
            # Count unique responses as proxy for cluster count
            unique_responses = len(set(s.strip().lower() for s in samples if s.strip()))
            cluster_counts.append(max(1, unique_responses))

    cluster_counts = cluster_counts[:2000]  # Cap at 2000
    arr = np.array(cluster_counts)
    histogram = {}
    for v in range(1, 6):
        histogram[str(v)] = int(np.sum(arr == v))

    return {
        "cluster_counts": cluster_counts,
        "mean_clusters": float(np.mean(arr)),
        "std_clusters": float(np.std(arr)),
        "n_singleton": int(np.sum(arr == 1)),
        "histogram": histogram,
    }


def pearson_r_bootstrap_ci(
    te: np.ndarray,
    se: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Pearson r with Fisher z-transform bootstrap 95% CI.
    Returns: {r_obs, ci_lower, ci_upper, r_boot, gate_pass}
    gate_pass = (ci_upper < 0.9)
    """
    N = len(te)
    r_obs, _ = stats.pearsonr(te, se)

    rng = np.random.default_rng(seed)
    z_boot = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, N, size=N)
        r_i, _ = stats.pearsonr(te[idx], se[idx])
        # Fisher z-transform with clipping to avoid inf
        z_i = np.arctanh(np.clip(r_i, -0.9999, 0.9999))
        z_boot.append(z_i)

    z_lower, z_upper = np.percentile(z_boot, [2.5, 97.5])
    ci_lower = float(np.tanh(z_lower))
    ci_upper = float(np.tanh(z_upper))
    r_boot_original = [float(np.tanh(z)) for z in z_boot]

    gate_pass = evaluate_gate(ci_upper, threshold=0.9)

    return {
        "r_obs": float(r_obs),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "r_boot": r_boot_original,
        "gate_pass": gate_pass,
    }


def evaluate_gate(ci_upper: float, threshold: float = 0.9, degenerate: bool = False) -> bool:
    """Return True if ci_upper < threshold (TE and SE are NOT interchangeable)."""
    if degenerate:
        return True
    return ci_upper < threshold


def spearman_rho(te: np.ndarray, se: np.ndarray) -> Tuple[float, float]:
    """Return (rho, p_value) via scipy.stats.spearmanr."""
    result = stats.spearmanr(te, se)
    return float(result.statistic), float(result.pvalue)
