import json
import numpy as np
from typing import Dict, Any, List, Tuple


def compute_pointwise_divergence(te: np.ndarray, se: np.ndarray) -> np.ndarray:
    """Return |te - se| per example, shape (N,)."""
    return np.abs(te - se)


def identify_high_divergence(
    divergence: np.ndarray,
    sigma_multiplier: float = 1.0,
) -> Tuple[np.ndarray, float]:
    """
    threshold = mean + sigma_multiplier * std
    Returns: (high_div_indices, threshold)
    """
    threshold = float(np.mean(divergence) + sigma_multiplier * np.std(divergence))
    high_div_indices = np.where(divergence > threshold)[0]
    return high_div_indices, threshold


def load_stochastic_samples(path: str) -> List[Dict]:
    """Load stochastic_samples.jsonl. Each line: {id: int, samples: List[str]}."""
    records = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def compute_ttr(samples: List[str]) -> float:
    """
    TTR = len(unique_tokens) / len(all_tokens) across concatenated samples.
    Tokenize by whitespace split + lowercase.
    """
    all_tokens = []
    for s in samples:
        all_tokens.extend(s.lower().split())
    if not all_tokens:
        return 0.0
    unique_tokens = set(all_tokens)
    return len(unique_tokens) / len(all_tokens)


def compute_ttr_by_group(
    samples_data: List[Dict],
    high_div_indices: np.ndarray,
) -> Dict[str, float]:
    """
    Compute mean TTR for high-divergence vs low-divergence groups.
    Returns: {mean_ttr_high_div, mean_ttr_low_div, n_high, n_low}
    """
    high_set = set(int(i) for i in high_div_indices)
    ttr_high: List[float] = []
    ttr_low: List[float] = []

    for i, record in enumerate(samples_data):
        samples = record.get("samples", [])
        ttr = compute_ttr(samples)
        rec_id = record.get("id", i)
        if int(rec_id) in high_set or i in high_set:
            ttr_high.append(ttr)
        else:
            ttr_low.append(ttr)

    mean_high = float(np.mean(ttr_high)) if ttr_high else 0.0
    mean_low = float(np.mean(ttr_low)) if ttr_low else 0.0

    return {
        "mean_ttr_high_div": mean_high,
        "mean_ttr_low_div": mean_low,
        "n_high": len(ttr_high),
        "n_low": len(ttr_low),
    }
