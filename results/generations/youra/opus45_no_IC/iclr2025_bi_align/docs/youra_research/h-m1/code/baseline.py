"""Shuffled baseline and permutation test for H-M1."""

import numpy as np
from scipy.stats import ttest_1samp
from typing import List, Tuple, Dict
from tqdm import tqdm

from config import N_PERMUTATIONS, SEED
from lagcorr import compute_lagged_correlation


def shuffle_baseline(ai_complexity: List[float], seed: int = None) -> List[float]:
    """np.random.shuffle copy of ai_complexity."""
    rng = np.random.default_rng(seed)
    shuffled = np.array(ai_complexity).copy()
    rng.shuffle(shuffled)
    return shuffled.tolist()


def run_permutation_test(
    trajectories: List[Tuple[List[float], List[float]]],
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED
) -> Dict:
    """Run permutation test on shuffled AI turns. Returns null distribution stats."""
    rng = np.random.default_rng(seed)
    shuffled_rs = []

    n_convos = len(trajectories)

    for i in tqdm(range(n_permutations), desc="Permutation test"):
        convo_idx = i % n_convos
        user, ai = trajectories[convo_idx]
        ai_shuf = shuffle_baseline(ai, seed=rng.integers(1e9))
        r, _ = compute_lagged_correlation(user, ai_shuf, lag=1)
        if not np.isnan(r):
            shuffled_rs.append(r)

    shuffled_arr = np.array(shuffled_rs)

    if len(shuffled_arr) < 10:
        return {
            'shuffled_lag1_rs': shuffled_rs,
            'null_mean': np.nan,
            'null_std': np.nan,
            'null_p': 1.0
        }

    t_stat, null_p = ttest_1samp(shuffled_arr, 0)

    return {
        'shuffled_lag1_rs': shuffled_rs,
        'null_mean': float(np.mean(shuffled_arr)),
        'null_std': float(np.std(shuffled_arr)),
        'null_p': float(null_p)
    }
