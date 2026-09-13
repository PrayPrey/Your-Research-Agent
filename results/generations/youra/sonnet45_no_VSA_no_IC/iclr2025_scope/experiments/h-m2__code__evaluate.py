"""HotpotQA evaluation: F1, EM, statistical tests."""
import re
import string
from collections import Counter
from typing import List, Dict
from scipy import stats


def normalize_answer(s: str) -> str:
    """Normalize answer string for HotpotQA evaluation.

    Normalization:
        - Lowercase
        - Remove articles (a, an, the)
        - Remove punctuation
        - Remove extra whitespace
    """
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def compute_f1(prediction: str, ground_truths: List[str]) -> float:
    """Token-level F1 score (max over multiple ground truths).

    Args:
        prediction: Model prediction
        ground_truths: List of valid answers

    Returns:
        F1 score ∈ [0, 1]
    """
    pred_tokens = normalize_answer(prediction).split()
    max_f1 = 0.0

    for gt in ground_truths:
        gt_tokens = normalize_answer(gt).split()
        common = Counter(pred_tokens) & Counter(gt_tokens)
        num_same = sum(common.values())

        if num_same == 0:
            f1 = 0.0
        else:
            precision = num_same / len(pred_tokens) if pred_tokens else 0.0
            recall = num_same / len(gt_tokens) if gt_tokens else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        max_f1 = max(max_f1, f1)

    return max_f1


def compute_exact_match(prediction: str, ground_truths: List[str]) -> float:
    """Binary exact match after normalization.

    Args:
        prediction: Model prediction
        ground_truths: List of valid answers

    Returns:
        1.0 if exact match, 0.0 otherwise
    """
    norm_pred = normalize_answer(prediction)
    for gt in ground_truths:
        if norm_pred == normalize_answer(gt):
            return 1.0
    return 0.0


def compute_significance(
    diversity_scores: List[float],
    relevance_scores: List[float],
    alpha: float = 0.05
) -> Dict[str, float]:
    """Paired t-test for F1 score difference.

    Args:
        diversity_scores: F1 scores from diversity-aware variant
        relevance_scores: F1 scores from relevance-only variant
        alpha: Significance threshold

    Returns:
        {
            't_statistic': float,
            'p_value': float,
            'significant': bool,
            'effect_size': float,  # Cohen's d
            'mean_diff': float
        }
    """
    if len(diversity_scores) != len(relevance_scores):
        raise ValueError("Score lists must have same length")

    # Paired t-test (two-tailed)
    t_stat, p_value = stats.ttest_rel(diversity_scores, relevance_scores)

    # Cohen's d (effect size)
    diffs = [d - r for d, r in zip(diversity_scores, relevance_scores)]
    mean_diff = sum(diffs) / len(diffs)
    std_diff = (sum((x - mean_diff) ** 2 for x in diffs) / len(diffs)) ** 0.5
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0

    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'significant': p_value < alpha,
        'effect_size': cohens_d,
        'mean_diff': mean_diff
    }
