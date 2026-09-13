"""Correlation analysis module."""
import numpy as np
from scipy import stats
from data import extract_assistant_response
from collab_score import compute_collab_score_v2
import config

def compute_correlation(dataset, n_samples: int = None) -> dict:
    """Compute Pearson correlation between collab_score and preference labels."""
    n_samples = n_samples or config.SAMPLE_SIZE

    chosen_scores = []
    rejected_scores = []

    for i, example in enumerate(dataset):
        if i >= n_samples:
            break
        chosen_text = extract_assistant_response(example['chosen'])
        rejected_text = extract_assistant_response(example['rejected'])
        chosen_scores.append(compute_collab_score_v2(chosen_text))
        rejected_scores.append(compute_collab_score_v2(rejected_text))

    all_scores = chosen_scores + rejected_scores
    all_labels = [1] * len(chosen_scores) + [0] * len(rejected_scores)

    correlation, p_value = stats.pearsonr(all_scores, all_labels)

    return {
        'correlation': float(correlation),
        'p_value': float(p_value),
        'chosen_mean': float(np.mean(chosen_scores)),
        'chosen_std': float(np.std(chosen_scores)),
        'rejected_mean': float(np.mean(rejected_scores)),
        'rejected_std': float(np.std(rejected_scores)),
        'gate_passed': abs(correlation) < config.CORRELATION_THRESHOLD,
        'n_samples': len(chosen_scores),
        'chosen_scores': chosen_scores,
        'rejected_scores': rejected_scores,
    }
