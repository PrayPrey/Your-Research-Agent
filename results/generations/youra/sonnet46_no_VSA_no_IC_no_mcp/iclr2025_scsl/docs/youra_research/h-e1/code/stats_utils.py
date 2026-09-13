import json
import logging
import os
from itertools import combinations

import numpy as np
from scipy import stats

from config import BONFERRONI_N, GATE_ALPHA, GATE_MIN_DIFF


def run_anova(ratios):
    """scipy.stats.f_oneway; returns (f_stat, p_value)."""
    arrays = [ratios[p] for p in ratios]
    f_stat, p_value = stats.f_oneway(*arrays)
    return float(f_stat), float(p_value)


def pairwise_tests(ratios, n_bonferroni=BONFERRONI_N):
    """
    6 pairwise ttest_ind with Bonferroni correction and Cohen's d.
    Returns list of dicts: {pair, t, p_raw, p_bonf, cohens_d, mean_diff}
    """
    results = []
    paradigms = list(ratios.keys())
    for p1, p2 in combinations(paradigms, 2):
        a = np.array(ratios[p1])
        b = np.array(ratios[p2])
        t, p_raw = stats.ttest_ind(a, b)
        p_bonf = min(float(p_raw) * n_bonferroni, 1.0)
        pooled_std = np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 2)
        d = float((a.mean() - b.mean()) / pooled_std) if pooled_std > 0 else 0.0
        results.append({
            'pair': f'{p1}_vs_{p2}',
            't': float(t),
            'p_raw': float(p_raw),
            'p_bonf': float(p_bonf),
            'cohens_d': float(d),
            'mean_diff': float(abs(a.mean() - b.mean())),
        })
    return results


def check_gate(pair_results, alpha=GATE_ALPHA, min_diff=GATE_MIN_DIFF):
    """Returns (gate_satisfied: bool, passing_pairs: list[dict])"""
    passing = []
    for r in pair_results:
        if r['p_bonf'] < alpha and r['mean_diff'] >= min_diff:
            passing.append(r)
            logging.info(
                f"GATE PASS: {r['pair']} p_bonf={r['p_bonf']:.4f} diff={r['mean_diff']:.4f}"
            )
    gate_ok = len(passing) > 0
    if not gate_ok:
        logging.warning("GATE FAIL: no pair meets p_bonf<0.05 AND diff>=0.02 — route to Phase 0")
    else:
        logging.info(f"GATE SATISFIED: {len(passing)} pair(s) pass")
    return gate_ok, passing


def summarize(ratios):
    """Mean ± std per paradigm."""
    return {
        p: {'mean': float(np.mean(v)), 'std': float(np.std(v, ddof=1))}
        for p, v in ratios.items()
    }


def export_results(ratios, anova_result, pair_results, gate_ok, passing_pairs, out_path):
    """Save stats JSON to out_path."""
    f_stat, p_anova = anova_result
    summary = summarize(ratios)
    payload = {
        'anova': {'f_stat': f_stat, 'p_value': p_anova},
        'pairwise': pair_results,
        'summary': summary,
        'gate': {
            'satisfied': gate_ok,
            'passing_pairs': [r['pair'] for r in passing_pairs],
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)
    logging.info(f"Stats exported to {out_path}")
