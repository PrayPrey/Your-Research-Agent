"""Ablation studies for H-M2 (only run if gate fails)."""

import numpy as np
from scipy import stats
from correlation import compute_correlation


def extreme_formality_filter(human_scores: list, ai_scores: list,
                              low_q: float = 0.25, high_q: float = 0.75) -> dict:
    """Filter to extreme formality humans and recompute correlation."""
    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    low_thresh = np.quantile(human_arr, low_q)
    high_thresh = np.quantile(human_arr, high_q)

    extreme_mask = (human_arr <= low_thresh) | (human_arr >= high_thresh)

    extreme_human = human_arr[extreme_mask].tolist()
    extreme_ai = ai_arr[extreme_mask].tolist()

    if len(extreme_human) < 100:
        return {'error': 'Insufficient samples after filtering'}

    results = compute_correlation(extreme_human, extreme_ai)
    results['filter_type'] = 'extreme_formality'
    results['low_q'] = low_q
    results['high_q'] = high_q

    return results


def length_partial_correlation(human_scores: list, ai_scores: list,
                                 human_texts: list, ai_texts: list) -> dict:
    """Partial correlation controlling for message length."""
    human_lens = np.array([len(t) for t in human_texts])
    ai_lens = np.array([len(t) for t in ai_texts])

    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    def partial_corr(x, y, z):
        """Compute partial correlation of x and y controlling for z."""
        x_resid = x - np.polyval(np.polyfit(z, x, 1), z)
        y_resid = y - np.polyval(np.polyfit(z, y, 1), z)
        return stats.pearsonr(x_resid, y_resid)

    r_human_len, p_human_len = partial_corr(human_arr, ai_arr, human_lens)
    r_ai_len, p_ai_len = partial_corr(human_arr, ai_arr, ai_lens)
    r_both_len, p_both_len = partial_corr(human_arr, ai_arr, human_lens + ai_lens)

    return {
        'control_human_len': {'r': float(r_human_len), 'p': float(p_human_len)},
        'control_ai_len': {'r': float(r_ai_len), 'p': float(p_ai_len)},
        'control_both_len': {'r': float(r_both_len), 'p': float(p_both_len)},
    }


def run_ablations(human_scores: list, ai_scores: list, pairs: list) -> dict:
    """Run all ablation studies."""
    results = {}

    results['extreme_filter'] = extreme_formality_filter(human_scores, ai_scores)

    human_texts = [p[0] for p in pairs]
    ai_texts = [p[1] for p in pairs]
    results['length_control'] = length_partial_correlation(human_scores, ai_scores,
                                                            human_texts, ai_texts)

    return results
