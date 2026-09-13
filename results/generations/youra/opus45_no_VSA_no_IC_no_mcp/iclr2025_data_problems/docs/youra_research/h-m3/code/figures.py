"""Visualization for dose-response analysis."""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from dose_response import DoseResponseResult

def plot_dose_response_curve(
    thresholds: np.ndarray,
    scores_matrix: np.ndarray,
    result: DoseResponseResult,
    save_path: str = "figures/dose_response_curve.png"
) -> None:
    """Primary figure: dose-response curve with CI band."""
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    mean_scores = scores_matrix.mean(axis=1)
    std_scores = scores_matrix.std(axis=1)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(thresholds, mean_scores, yerr=std_scores, fmt='o',
                capsize=5, label='Observed (mean ± std)', color='#2563eb')

    x_fit = np.linspace(0, 90, 200)
    x_norm = x_fit / 100.0
    coeffs = result.model_coefficients[result.best_model]
    poly = np.poly1d(coeffs)
    y_fit = poly(x_norm)
    ax.plot(x_fit, y_fit, '-', color='#dc2626', linewidth=2,
            label=f'Best fit: {result.best_model}')

    ax.axvline(result.optimal_threshold, color='#16a34a', linestyle='--',
               label=f'Optimal: p{result.optimal_threshold:.0f}')
    ax.axvspan(result.confidence_interval[0], result.confidence_interval[1],
               alpha=0.2, color='#16a34a', label='95% CI')

    ax.set_xlabel('Perplexity Filter Threshold (percentile)', fontsize=12)
    ax.set_ylabel('Benchmark Ensemble Score', fontsize=12)
    ax.set_title('Dose-Response Curve: Quality-Diversity Tradeoff', fontsize=14)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")

def plot_model_comparison(
    aic_values: dict,
    bic_values: dict,
    save_path: str = "figures/model_comparison.png"
) -> None:
    """AIC/BIC comparison bar chart."""
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    models = list(aic_values.keys())
    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, [aic_values[m] for m in models], width, label='AIC')
    ax.bar(x + width/2, [bic_values[m] for m in models], width, label='BIC')

    ax.set_ylabel('Information Criterion')
    ax.set_xlabel('Model')
    ax.set_title('Model Selection: AIC vs BIC')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")

def plot_bootstrap_distribution(
    thresholds: np.ndarray,
    scores_matrix: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
    save_path: str = "figures/bootstrap_distribution.png"
) -> None:
    """Bootstrap threshold distribution histogram."""
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    np.random.seed(seed)
    n_seeds = scores_matrix.shape[1]
    optimal_thresholds = []

    for _ in range(n_bootstrap):
        seed_idx = np.random.choice(n_seeds, n_seeds, replace=True)
        resampled = scores_matrix[:, seed_idx].mean(axis=1)
        idx = np.argmax(resampled)
        optimal_thresholds.append(thresholds[idx])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(optimal_thresholds, bins=20, edgecolor='black', alpha=0.7)
    ax.axvline(np.mean(optimal_thresholds), color='red', linestyle='--',
               label=f'Mean: {np.mean(optimal_thresholds):.1f}')
    ax.set_xlabel('Optimal Threshold (percentile)')
    ax.set_ylabel('Frequency')
    ax.set_title('Bootstrap Distribution of Optimal Threshold')
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")
