"""Evaluation metrics and gate checking for h-m3"""
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error
from typing import Dict, Tuple
from config import ExperimentConfig

def calculate_correlations(
    human_scores: np.ndarray,
    ai_predictions: np.ndarray
) -> Dict[str, float]:
    """
    Calculate correlation metrics between human scores and AI predictions

    Args:
        human_scores: Ground truth human scores (0-10 scale)
        ai_predictions: Model predictions (0-10 scale)

    Returns:
        Dictionary with correlation metrics
    """
    # Spearman correlation (primary metric)
    rho, p_value = spearmanr(human_scores, ai_predictions)

    # Pearson correlation (secondary)
    pearson_r, pearson_p = pearsonr(human_scores, ai_predictions)

    # Mean absolute error
    mae = mean_absolute_error(human_scores, ai_predictions)

    return {
        'spearman_rho': float(rho),
        'spearman_p': float(p_value),
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'mae': float(mae),
        'n_samples': len(human_scores)
    }

def check_gate_criteria(
    metrics: Dict[str, float],
    config: ExperimentConfig
) -> Tuple[bool, str]:
    """
    Check MUST_WORK gate criteria

    Gate Requirements:
    - Spearman correlation > 0.7
    - p-value < 0.05
    - Test set size >= 170 samples

    Returns:
        (gate_satisfied, explanation)
    """
    rho = metrics['spearman_rho']
    p_value = metrics['spearman_p']
    n_samples = metrics['n_samples']

    checks = []

    # Check 1: Correlation threshold
    if rho > config.gate_correlation_threshold:
        checks.append(f"✓ Spearman ρ={rho:.3f} > {config.gate_correlation_threshold}")
    else:
        checks.append(f"✗ Spearman ρ={rho:.3f} ≤ {config.gate_correlation_threshold}")

    # Check 2: Statistical significance
    if p_value < config.gate_pvalue_threshold:
        checks.append(f"✓ p-value={p_value:.4f} < {config.gate_pvalue_threshold}")
    else:
        checks.append(f"✗ p-value={p_value:.4f} ≥ {config.gate_pvalue_threshold}")

    # Check 3: Sample size
    min_samples = config.data.min_test_samples
    if n_samples >= min_samples:
        checks.append(f"✓ Test samples={n_samples} >= {min_samples}")
    else:
        checks.append(f"✗ Test samples={n_samples} < {min_samples}")

    # Gate decision
    gate_satisfied = (
        rho > config.gate_correlation_threshold and
        p_value < config.gate_pvalue_threshold and
        n_samples >= min_samples
    )

    explanation = "\n".join(checks)
    return gate_satisfied, explanation

def compare_with_baseline(
    metrics: Dict[str, float],
    baseline_corr: float
) -> Dict[str, float]:
    """
    Compare supervised model with zero-shot baseline (from h-e1)

    Args:
        metrics: Current model metrics
        baseline_corr: h-e1 baseline AI-human correlation (0.485)

    Returns:
        Comparison metrics
    """
    improvement = metrics['spearman_rho'] - baseline_corr
    improvement_pct = (improvement / baseline_corr) * 100

    return {
        'baseline_correlation': baseline_corr,
        'supervised_correlation': metrics['spearman_rho'],
        'absolute_improvement': improvement,
        'relative_improvement_pct': improvement_pct
    }

if __name__ == "__main__":
    # Test with dummy data
    human = np.array([7.0, 5.0, 8.0, 6.0, 9.0] * 40)  # 200 samples
    ai = human + np.random.normal(0, 0.5, len(human))  # High correlation

    metrics = calculate_correlations(human, ai)
    print(f"Spearman ρ: {metrics['spearman_rho']:.3f}")
    print(f"p-value: {metrics['spearman_p']:.4f}")

    from config import get_config
    config = get_config()
    gate_ok, explanation = check_gate_criteria(metrics, config)
    print(f"\nGate satisfied: {gate_ok}")
    print(explanation)

    print("\n✓ Evaluation module validated")
