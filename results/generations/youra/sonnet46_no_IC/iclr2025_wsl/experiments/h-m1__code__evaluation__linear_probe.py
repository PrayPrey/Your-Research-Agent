"""
Linear probe evaluation: RidgeCV R² for ViT property prediction.
Compares SANE, EquiSSL (monomial), EquiSSL-perm (permutation).
"""
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split
from scipy import stats


@dataclass
class ProbeResult:
    r2_per_seed: List[float]
    r2_mean: float
    r2_std: float
    model_name: str


@dataclass
class StatTestResult:
    t_stat: float
    p_value: float
    significant: bool
    comparison: str


def evaluate_linear_probe(embeddings_per_seed, labels, alphas=None,
                           test_frac=0.2, random_state=42):
    """
    Run RidgeCV linear probe for each seed's embeddings.
    embeddings_per_seed: list of ndarray (N, D) per seed
    labels: ndarray (N,)
    Returns ProbeResult.
    """
    if alphas is None:
        alphas = [0.1, 1.0, 10.0, 100.0]

    r2_scores = []
    for i, emb in enumerate(embeddings_per_seed):
        X_tr, X_te, y_tr, y_te = train_test_split(
            emb, labels, test_size=test_frac, random_state=random_state + i)
        clf = RidgeCV(alphas=alphas, cv=5)
        clf.fit(X_tr, y_tr)
        r2 = clf.score(X_te, y_te)
        r2_scores.append(float(r2))

    return ProbeResult(
        r2_per_seed=r2_scores,
        r2_mean=float(np.mean(r2_scores)),
        r2_std=float(np.std(r2_scores)),
        model_name=''
    )


def evaluate_all_models(embeddings_dict, labels, seeds, alphas=None):
    """
    Evaluate linear probe for all models.
    embeddings_dict: {'sane_seed0': arr, 'equi_seed0': arr, 'equi_perm_seed0': arr, ...}
    Returns dict[model_name -> ProbeResult].
    """
    results = {}
    for model_name in ['sane', 'equi', 'equi_perm']:
        per_seed = []
        for seed in seeds:
            key = f'{model_name}_seed{seed}'
            if key in embeddings_dict:
                per_seed.append(embeddings_dict[key])
        if not per_seed:
            print(f'  WARNING: no embeddings for {model_name}, skipping')
            continue
        result = evaluate_linear_probe(per_seed, labels, alphas=alphas)
        result.model_name = model_name
        results[model_name] = result
        print(f'  {model_name}: R²={result.r2_mean:.4f} ± {result.r2_std:.4f} '
              f'(seeds: {[f"{r:.4f}" for r in result.r2_per_seed]})')
    return results


def paired_ttest(r2_graph, r2_sane):
    """Paired t-test: is graph R² > SANE R²? One-tailed."""
    if len(r2_graph) < 2 or len(r2_sane) < 2:
        # Not enough data — use effect size
        diff = np.mean(r2_graph) - np.mean(r2_sane)
        return StatTestResult(t_stat=float(diff), p_value=0.5,
                              significant=False, comparison='insufficient_data')
    # One-sample t-test on differences
    diffs = np.array(r2_graph) - np.array(r2_sane[:len(r2_graph)])
    t_stat, p_two = stats.ttest_1samp(diffs, 0.0)
    p_one = p_two / 2 if t_stat > 0 else 1.0 - p_two / 2
    return StatTestResult(
        t_stat=float(t_stat),
        p_value=float(p_one),
        significant=bool(p_one < 0.05),
        comparison=''
    )


def run_significance_tests(results):
    """
    Compare each graph model vs SANE baseline.
    Returns dict of StatTestResult.
    """
    stat_tests = {}
    sane_r2 = results.get('sane')
    if sane_r2 is None:
        print('  WARNING: no SANE results for significance testing')
        return stat_tests

    for model_name in ['equi', 'equi_perm']:
        if model_name not in results:
            continue
        test = paired_ttest(results[model_name].r2_per_seed,
                            sane_r2.r2_per_seed)
        test.comparison = f'{model_name}_vs_sane'
        stat_tests[model_name] = test
        sig = '✓' if test.significant else '✗'
        print(f'  {model_name} vs SANE: t={test.t_stat:.3f} '
              f'p={test.p_value:.4f} {sig}')
    return stat_tests


def evaluate_gate(results, stat_tests):
    """
    MUST_WORK gate: does the methodology work?
    PASS: at least one graph model achieves R² > SANE (p<0.05 or notable margin).
    PARTIAL: some improvement but not significant.
    FAIL: no improvement at all.
    """
    sane = results.get('sane')
    if sane is None:
        return 'FAIL'

    sane_r2 = sane.r2_mean
    improvements = []
    significant = []

    for model_name in ['equi', 'equi_perm']:
        if model_name not in results:
            continue
        r2 = results[model_name].r2_mean
        improvement = r2 - sane_r2
        improvements.append(improvement)
        test = stat_tests.get(model_name)
        is_sig = test.significant if test else False
        significant.append(is_sig)
        print(f'  Gate: {model_name} improvement={improvement:+.4f} '
              f'significant={is_sig}')

    if not improvements:
        return 'FAIL'

    any_sig = any(significant)
    any_improvement = any(d > 0 for d in improvements)
    notable_improvement = any(d > 0.02 for d in improvements)

    if any_sig or notable_improvement:
        return 'PASS'
    elif any_improvement:
        return 'PARTIAL'
    else:
        return 'FAIL'
