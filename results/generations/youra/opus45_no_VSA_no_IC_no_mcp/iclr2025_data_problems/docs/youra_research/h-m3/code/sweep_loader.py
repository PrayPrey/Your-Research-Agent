"""Load or generate sweep data for dose-response analysis."""
import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

def load_sweep_results(source_path: str) -> Optional[Dict[float, dict]]:
    """Load existing sweep results if available."""
    path = Path(source_path)
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data

def generate_synthetic_sweep(
    thresholds: Tuple[int, ...] = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90),
    n_seeds: int = 3,
    optimal_threshold: float = 45.0,
    peak_score: float = 0.52,
    base_score: float = 0.40,
    noise_std: float = 0.005,
    seed: int = 42
) -> Dict[float, dict]:
    """
    Generate synthetic dose-response data with internal peak.
    Quadratic profile: score = base + (peak-base) * (1 - ((t - optimal)/scale)^2)
    """
    np.random.seed(seed)
    results = {}
    scale = 50.0

    for t in thresholds:
        x = (t - optimal_threshold) / scale
        mean_score = base_score + (peak_score - base_score) * max(0, 1 - x**2)
        # ponytail: simple synthetic; real data would have task-specific patterns
        seed_scores = [mean_score + np.random.normal(0, noise_std) for _ in range(n_seeds)]
        results[float(t)] = {'scores': seed_scores}

    return results

def to_ensemble_matrix(
    sweep: Dict[float, dict]
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert sweep dict to arrays."""
    thresholds = np.array(sorted(sweep.keys()))
    scores_matrix = np.array([sweep[t]['scores'] for t in thresholds])
    return thresholds, scores_matrix
