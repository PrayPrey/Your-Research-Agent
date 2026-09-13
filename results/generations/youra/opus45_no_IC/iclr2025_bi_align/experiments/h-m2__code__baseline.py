"""Permutation baseline for H-M2 experiment."""

import numpy as np
from scipy import stats
from config import N_PERMUTATIONS, SEED


def run_permutation_test(human_scores: list, ai_scores: list,
                          n_permutations: int = N_PERMUTATIONS, seed: int = SEED) -> dict:
    """Run permutation test to establish null distribution."""
    np.random.seed(seed)

    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    observed_r, _ = stats.pearsonr(human_arr, ai_arr)

    null_rs = []
    for _ in range(n_permutations):
        shuffled_ai = np.random.permutation(ai_arr)
        null_r, _ = stats.pearsonr(human_arr, shuffled_ai)
        null_rs.append(null_r)

    null_rs = np.array(null_rs)
    p_value = np.mean(np.abs(null_rs) >= np.abs(observed_r))

    return {
        'observed_r': float(observed_r),
        'null_mean': float(np.mean(null_rs)),
        'null_std': float(np.std(null_rs)),
        'null_p': float(p_value),
        'n_permutations': n_permutations,
        'exceeds_null': p_value < 0.05
    }
