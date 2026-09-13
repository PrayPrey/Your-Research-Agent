"""Evaluation metrics for LongBench QA"""

import re
import string
from collections import Counter
from typing import List, Dict
import scipy.stats as stats

def normalize_answer(s: str) -> str:
    """Remove articles, punctuation, extra whitespace"""
    s = s.lower()
    s = re.sub(r'\b(a|an|the)\b', ' ', s)
    s = ''.join(ch if ch not in string.punctuation else ' ' for ch in s)
    s = ' '.join(s.split())
    return s

def compute_f1(prediction: str, ground_truths: List[str]) -> float:
    """Token-level F1 score"""
    pred_tokens = normalize_answer(prediction).split()
    max_f1 = 0.0
    for gt in ground_truths:
        gt_tokens = normalize_answer(gt).split()
        common = Counter(pred_tokens) & Counter(gt_tokens)
        num_same = sum(common.values())
        if num_same == 0:
            f1 = 0.0
        else:
            precision = num_same / len(pred_tokens) if len(pred_tokens) > 0 else 0.0
            recall = num_same / len(gt_tokens) if len(gt_tokens) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        max_f1 = max(max_f1, f1)
    return max_f1

def compute_exact_match(prediction: str, ground_truths: List[str]) -> float:
    """Exact match after normalization"""
    pred_norm = normalize_answer(prediction)
    for gt in ground_truths:
        if pred_norm == normalize_answer(gt):
            return 1.0
    return 0.0

def compute_significance(
    provenance_scores: List[float],
    h2o_scores: List[float],
    alpha: float = 0.05
) -> Dict[str, float]:
    """Two-tailed t-test"""
    t_stat, p_value = stats.ttest_rel(provenance_scores, h2o_scores)
    return {
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'significant': bool(p_value < alpha)
    }

def aggregate_results(results: List[Dict]) -> Dict:
    """Compute aggregate statistics"""
    f1_scores = [r['f1'] for r in results]
    em_scores = [r['em'] for r in results]

    return {
        'f1_mean': float(np.mean(f1_scores)),
        'f1_std': float(np.std(f1_scores)),
        'em_mean': float(np.mean(em_scores)),
        'em_std': float(np.std(em_scores)),
        'n_samples': len(results)
    }

import numpy as np
