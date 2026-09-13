"""AUROC evaluation and statistical analysis for entropy discrimination.

This module computes AUROC, bootstrap CI, statistical tests, and calibration metrics.
"""

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from scipy import stats
from typing import Dict, Tuple


def compute_auroc_with_ci(
    labels: np.ndarray,
    scores: np.ndarray,
    n_bootstraps: int = 1000,
    seed: int = 42
) -> Dict:
    """Compute AUROC with bootstrap confidence interval.

    Parameters
    ----------
    labels : np.ndarray
        Binary labels (0=correct, 1=hallucinated)
    scores : np.ndarray
        Scores (higher for hallucinated)
    n_bootstraps : int
        Number of bootstrap iterations
    seed : int
        Random seed

    Returns
    -------
    Dict
        AUROC point estimate and 95% CI
    """
    rng = np.random.RandomState(seed)

    # Point estimate
    auroc = roc_auc_score(labels, scores)

    # Bootstrap
    auroc_samples = []
    n = len(labels)

    for _ in range(n_bootstraps):
        indices = rng.randint(0, n, n)
        try:
            boot_auroc = roc_auc_score(labels[indices], scores[indices])
            auroc_samples.append(boot_auroc)
        except ValueError:
            # Handle case where bootstrap sample has only one class
            continue

    ci_lower = np.percentile(auroc_samples, 2.5)
    ci_upper = np.percentile(auroc_samples, 97.5)

    return {
        'auroc': float(auroc),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'n_bootstraps': len(auroc_samples)
    }


def compute_statistical_tests(
    entropies: np.ndarray,
    labels: np.ndarray
) -> Dict:
    """Compute statistical significance tests.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels

    Returns
    -------
    Dict
        Test results (t-test, Mann-Whitney U, Cohen's d)
    """
    correct_entropies = entropies[labels == 0]
    hallucinated_entropies = entropies[labels == 1]

    # Two-sample t-test (one-tailed: hallucinated > correct)
    t_stat, p_value_twotail = stats.ttest_ind(
        hallucinated_entropies,
        correct_entropies,
        equal_var=False  # Welch's t-test
    )
    p_value = p_value_twotail / 2  # One-tailed

    # Mann-Whitney U test (non-parametric alternative)
    u_stat, p_value_mw = stats.mannwhitneyu(
        hallucinated_entropies,
        correct_entropies,
        alternative='greater'
    )

    # Cohen's d effect size
    mean_diff = np.mean(hallucinated_entropies) - np.mean(correct_entropies)
    pooled_std = np.sqrt(
        (np.var(correct_entropies) + np.var(hallucinated_entropies)) / 2
    )
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

    return {
        't_test': {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': bool(p_value < 0.05)
        },
        'mann_whitney_u': {
            'u_statistic': float(u_stat),
            'p_value': float(p_value_mw),
            'significant': bool(p_value_mw < 0.05)
        },
        'cohens_d': float(cohens_d),
        'effect_size_interpretation': (
            'large' if abs(cohens_d) >= 0.8 else
            'medium' if abs(cohens_d) >= 0.5 else
            'small' if abs(cohens_d) >= 0.2 else
            'negligible'
        )
    }


def compute_calibration_curve(
    entropies: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Compute calibration curve and Spearman correlation.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels
    n_bins : int
        Number of entropy bins

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, float]
        (bin_entropies, error_rates, spearman_rho)
    """
    # Bin tokens by entropy quantiles
    quantiles = np.linspace(0, 100, n_bins + 1)
    bin_edges = np.percentile(entropies, quantiles)

    bin_entropies = []
    error_rates = []

    for i in range(n_bins):
        mask = (entropies >= bin_edges[i]) & (entropies < bin_edges[i + 1])
        if i == n_bins - 1:  # Include upper edge in last bin
            mask = (entropies >= bin_edges[i]) & (entropies <= bin_edges[i + 1])

        if np.sum(mask) == 0:
            continue

        bin_entropy = np.mean(entropies[mask])
        error_rate = np.mean(labels[mask])

        bin_entropies.append(bin_entropy)
        error_rates.append(error_rate)

    bin_entropies = np.array(bin_entropies)
    error_rates = np.array(error_rates)

    # Compute Spearman correlation
    spearman_rho, _ = stats.spearmanr(bin_entropies, error_rates)

    return bin_entropies, error_rates, float(spearman_rho)


def compute_roc_curve(
    labels: np.ndarray,
    scores: np.ndarray
) -> Dict:
    """Compute ROC curve.

    Parameters
    ----------
    labels : np.ndarray
        Binary labels
    scores : np.ndarray
        Scores

    Returns
    -------
    Dict
        FPR, TPR, thresholds
    """
    fpr, tpr, thresholds = roc_curve(labels, scores)

    return {
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist(),
        'thresholds': thresholds.tolist()
    }


def evaluate_baseline_random(
    labels: np.ndarray,
    seed: int = 42
) -> Dict:
    """Evaluate random baseline.

    Parameters
    ----------
    labels : np.ndarray
        Binary labels
    seed : int
        Random seed

    Returns
    -------
    Dict
        Random baseline AUROC
    """
    rng = np.random.RandomState(seed)
    random_scores = rng.rand(len(labels))

    auroc = roc_auc_score(labels, random_scores)

    return {
        'auroc': float(auroc),
        'method': 'random'
    }


def evaluate_baseline_confidence(
    logits_list: list,
    labels: np.ndarray
) -> Dict:
    """Evaluate confidence-based baseline.

    Parameters
    ----------
    logits_list : list
        List of logits arrays
    labels : np.ndarray
        Binary labels

    Returns
    -------
    Dict
        Confidence baseline AUROC
    """
    from scipy.special import softmax

    # Compute max probability (confidence) for each token
    confidences = []
    for logits in logits_list:
        probs = softmax(logits)
        max_prob = np.max(probs)
        confidences.append(max_prob)

    confidences = np.array(confidences)

    # Use 1 - confidence as uncertainty score (higher for hallucinated)
    uncertainty_scores = 1.0 - confidences

    auroc = roc_auc_score(labels, uncertainty_scores)

    return {
        'auroc': float(auroc),
        'method': 'confidence'
    }


def evaluate_full_pipeline(
    entropies: np.ndarray,
    labels: np.ndarray,
    logits_list: list = None
) -> Dict:
    """Run full evaluation pipeline.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels
    logits_list : list, optional
        Logits for baseline evaluation

    Returns
    -------
    Dict
        Complete evaluation results
    """
    results = {}

    # AUROC with CI
    print("Computing AUROC with bootstrap CI...")
    results['auroc'] = compute_auroc_with_ci(labels, entropies)

    # Statistical tests
    print("Running statistical tests...")
    results['statistical_tests'] = compute_statistical_tests(entropies, labels)

    # Calibration curve
    print("Computing calibration curve...")
    bin_entropies, error_rates, spearman_rho = compute_calibration_curve(
        entropies, labels
    )
    results['calibration'] = {
        'bin_entropies': bin_entropies.tolist(),
        'error_rates': error_rates.tolist(),
        'spearman_rho': float(spearman_rho)
    }

    # ROC curve
    print("Computing ROC curve...")
    results['roc_curve'] = compute_roc_curve(labels, entropies)

    # Baselines
    print("Evaluating baselines...")
    results['baselines'] = {
        'random': evaluate_baseline_random(labels)
    }

    if logits_list is not None:
        results['baselines']['confidence'] = evaluate_baseline_confidence(
            logits_list, labels
        )

    return results


def determine_gate_decision(results: Dict) -> Dict:
    """Determine gate decision based on success criteria.

    Parameters
    ----------
    results : Dict
        Evaluation results

    Returns
    -------
    Dict
        Gate decision and reasoning
    """
    # Extract metrics
    auroc = results['auroc']['auroc']
    ci_lower = results['auroc']['ci_lower']
    p_value = results['statistical_tests']['t_test']['p_value']
    cohens_d = results['statistical_tests']['cohens_d']
    spearman_rho = results['calibration']['spearman_rho']

    # Check thresholds
    checks = {
        'auroc_threshold': {
            'threshold': 0.80,
            'actual': float(auroc),
            'met': bool(auroc >= 0.80 and ci_lower >= 0.80)
        },
        'p_value_threshold': {
            'threshold': 0.05,
            'actual': float(p_value),
            'met': bool(p_value < 0.05)
        },
        'effect_size_threshold': {
            'threshold': 0.50,
            'actual': float(cohens_d),
            'met': bool(cohens_d > 0.50)
        },
        'calibration_threshold': {
            'threshold': 0.80,
            'actual': float(spearman_rho),
            'met': bool(spearman_rho > 0.80)
        }
    }

    # Determine decision
    all_met = all(c['met'] for c in checks.values())
    some_met = any(c['met'] for c in checks.values())

    if all_met:
        decision = 'PASS'
        interpretation = 'All success criteria met. Token-level entropy provides reliable discrimination.'
    elif auroc >= 0.70:
        decision = 'PARTIAL'
        interpretation = f'Weak signal detected (AUROC={auroc:.3f}). Some criteria unmet. Modification attempt recommended.'
    else:
        decision = 'FAIL'
        interpretation = f'No discriminative power (AUROC={auroc:.3f}). Fundamental flaw in approach.'

    return {
        'decision': decision,
        'success_criteria': checks,
        'interpretation': interpretation
    }
