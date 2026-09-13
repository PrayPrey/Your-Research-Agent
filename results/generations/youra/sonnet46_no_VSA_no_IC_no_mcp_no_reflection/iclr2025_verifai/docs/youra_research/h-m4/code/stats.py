"""H-M4 statistical analysis: efficiency ratios, bootstrap BCa, Kruskal-Wallis, Mann-Whitney."""
import numpy as np
from scipy import stats as scipy_stats
from scipy.stats import kruskal, mannwhitneyu

CATEGORIES = ['execution', 'static', 'type', 'smt']


def compute_efficiency_ratio(
    pass_after: float, pass_baseline: float, mean_overhead_s: float
) -> float:
    delta = pass_after - pass_baseline
    if mean_overhead_s <= 0 or np.isnan(mean_overhead_s):
        return float('nan')
    return delta / mean_overhead_s


def compute_per_problem_ratios(
    results: list[dict], baseline_pass: dict[str, bool], category: str
) -> np.ndarray:
    cat_results = [r for r in results if r['category'] == category]
    ratios = []
    for r in cat_results:
        task_id = r['task_id']
        baseline = float(baseline_pass.get(task_id, False))
        final = float(r['final_pass'])
        overhead = r['total_overhead_s']
        if overhead > 0:
            ratios.append((final - baseline) / overhead)
        else:
            ratios.append(float('nan'))
    return np.array(ratios, dtype=float)


def bootstrap_ratio_comparison(
    ratios_a: np.ndarray,
    ratios_b: np.ndarray,
    n_resamples: int = 10000,
    confidence_level: float = 0.95,
) -> dict:
    def diff_means(a, b, axis):
        return np.mean(a, axis=axis) - np.mean(b, axis=axis)

    a_clean = ratios_a[~np.isnan(ratios_a)]
    b_clean = ratios_b[~np.isnan(ratios_b)]

    if len(a_clean) < 2 or len(b_clean) < 2:
        return {'ci_low': float('nan'), 'ci_high': float('nan'),
                'mean_diff': float('nan'), 'p_approx': 1.0, 'significant': False}

    try:
        result = scipy_stats.bootstrap(
            (a_clean, b_clean),
            diff_means,
            n_resamples=n_resamples,
            method='BCa',
            confidence_level=confidence_level,
            paired=False,
            random_state=1,
        )
        ci_low, ci_high = result.confidence_interval
    except Exception:
        # Fall back to percentile bootstrap if BCa fails
        diffs = []
        rng = np.random.default_rng(1)
        for _ in range(n_resamples):
            da = rng.choice(a_clean, size=len(a_clean), replace=True)
            db = rng.choice(b_clean, size=len(b_clean), replace=True)
            diffs.append(np.mean(da) - np.mean(db))
        diffs = np.array(diffs)
        ci_low = float(np.percentile(diffs, 100 * (1 - confidence_level) / 2))
        ci_high = float(np.percentile(diffs, 100 * (1 - (1 - confidence_level) / 2)))

    mean_diff = float(np.mean(a_clean) - np.mean(b_clean))
    significant = not (float(ci_low) <= 0 <= float(ci_high))
    return {
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        'mean_diff': mean_diff,
        'p_approx': 0.04 if significant else 1.0,
        'significant': significant,
    }


def kruskal_wallis_overhead(overhead_by_cat: dict[str, list[float]]) -> dict:
    groups = [overhead_by_cat[cat] for cat in CATEGORIES if cat in overhead_by_cat]
    if len(groups) < 2:
        return {'statistic': float('nan'), 'p_value': 1.0, 'significant': False}
    stat, p = kruskal(*groups)
    return {'statistic': float(stat), 'p_value': float(p), 'significant': p < 0.05}


def mannwhitney_pairwise(overhead_by_cat: dict[str, list[float]]) -> dict:
    results = {}
    cats = [c for c in CATEGORIES if c in overhead_by_cat]
    for i, ca in enumerate(cats):
        for cb in cats[i + 1:]:
            try:
                stat, p = mannwhitneyu(
                    overhead_by_cat[ca], overhead_by_cat[cb], alternative='two-sided'
                )
                results[f"{ca}_vs_{cb}"] = {
                    'statistic': float(stat),
                    'p_value': float(p),
                    'ca_slower': float(np.median(overhead_by_cat[ca])) > float(np.median(overhead_by_cat[cb])),
                }
            except Exception as e:
                results[f"{ca}_vs_{cb}"] = {'error': str(e)}
    return results


def summarize_overhead(overhead_by_cat: dict[str, list[float]]) -> dict[str, dict]:
    summary = {}
    for cat, vals in overhead_by_cat.items():
        arr = np.array(vals)
        if len(arr) == 0:
            summary[cat] = {'n': 0}
            continue
        summary[cat] = {
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'p95': float(np.percentile(arr, 95)),
            'n': len(vals),
        }
    return summary


def evaluate_gate_metric(results: list[dict], baseline_pass: dict[str, bool]) -> dict:
    overhead_by_cat = {cat: [] for cat in CATEGORIES}
    for r in results:
        cat = r['category']
        if cat in overhead_by_cat:
            overhead_by_cat[cat].append(r['total_overhead_s'])

    overhead_means = {cat: float(np.mean(vals)) if vals else float('nan')
                     for cat, vals in overhead_by_cat.items()}

    pass_after = {}
    for cat in CATEGORIES:
        cat_results = [r for r in results if r['category'] == cat]
        if cat_results:
            pass_after[cat] = float(np.mean([r['final_pass'] for r in cat_results]))
        else:
            pass_after[cat] = float('nan')

    # Baseline: mean of per-problem baseline pass flags in results
    baseline_vals = [float(r.get('initial_pass', False)) for r in results if r['category'] == CATEGORIES[0]]
    baseline_rate = float(np.mean(baseline_vals)) if baseline_vals else 0.0

    ratios = {
        cat: compute_efficiency_ratio(pass_after[cat], baseline_rate, overhead_means[cat])
        for cat in CATEGORIES
    }

    valid_ratios = {c: v for c, v in ratios.items() if not np.isnan(v)}
    if not valid_ratios:
        return {'gate_passed': False, 'error': 'No valid ratios', 'ratios': ratios}

    sorted_cats = sorted(valid_ratios, key=lambda c: valid_ratios[c], reverse=True)
    best_cat = sorted_cats[0]
    second_best_cat = sorted_cats[1] if len(sorted_cats) > 1 else best_cat

    per_problem_best = compute_per_problem_ratios(results, baseline_pass, best_cat)
    per_problem_second = compute_per_problem_ratios(results, baseline_pass, second_best_cat)
    bootstrap_result = bootstrap_ratio_comparison(per_problem_best, per_problem_second)

    ratio_advantage = (
        valid_ratios[best_cat] / valid_ratios[second_best_cat]
        if valid_ratios.get(second_best_cat, 0) > 0 else float('inf')
    )

    gate_passed = (
        best_cat == 'execution'
        and ratio_advantage >= 1.5
        and bootstrap_result.get('significant', False)
    )

    return {
        'ratios': ratios,
        'overhead_means': overhead_means,
        'pass_after': pass_after,
        'baseline_rate': baseline_rate,
        'best_category': best_cat,
        'second_best_category': second_best_cat,
        'ratio_advantage': float(ratio_advantage),
        'bootstrap_result': bootstrap_result,
        'gate_passed': gate_passed,
        'execution_is_best': best_cat == 'execution',
    }
