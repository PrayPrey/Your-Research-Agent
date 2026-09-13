"""H-E1: Visualization - Gate Metrics + Supporting Figures"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List, Optional

from config import MODEL_FAMILY, RESULTS_PATH, ANALYSIS_PATH, FIGURES_DIR


FAMILY_COLORS = {
    "llama2": "#1f77b4",
    "llama3": "#ff7f0e",
    "mistral": "#2ca02c",
    "flan-t5": "#d62728",
    "phi": "#9467bd"
}


def plot_gate_metrics(
    results: Dict,
    analysis: Dict,
    out_path: str = f"{FIGURES_DIR}/gate_metrics.png"
) -> None:
    """Required: Scatter plot MC1 vs (1-ASR) with regression line and CI band."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    mc1 = np.array(results["mc1_acc"])
    robustness = np.array(results["robustness"])
    models = results["model"]

    mask = ~(np.isnan(mc1) | np.isnan(robustness))
    mc1_clean = mc1[mask]
    rob_clean = robustness[mask]
    models_clean = [m for m, valid in zip(models, mask) if valid]

    fig, ax = plt.subplots(figsize=(10, 8))

    for model, x, y in zip(models_clean, mc1_clean, rob_clean):
        family = MODEL_FAMILY.get(model, "unknown")
        color = FAMILY_COLORS.get(family, "#333333")
        ax.scatter(x, y, c=color, s=100, alpha=0.8, edgecolors='white', linewidth=1)

    slope, intercept, r, p, se = stats.linregress(mc1_clean, rob_clean)
    x_line = np.linspace(mc1_clean.min(), mc1_clean.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'k-', linewidth=2, label=f'Regression (r={r:.3f})')

    n = len(mc1_clean)
    y_pred = slope * mc1_clean + intercept
    residuals = rob_clean - y_pred
    mse = np.sum(residuals**2) / (n - 2)
    se_y = np.sqrt(mse * (1/n + (x_line - mc1_clean.mean())**2 / np.sum((mc1_clean - mc1_clean.mean())**2)))
    t_val = stats.t.ppf(0.975, n - 2)
    ci_upper = y_line + t_val * se_y
    ci_lower = y_line - t_val * se_y
    ax.fill_between(x_line, ci_lower, ci_upper, alpha=0.2, color='gray', label='95% CI')

    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='r=0.5 threshold')

    for family, color in FAMILY_COLORS.items():
        ax.scatter([], [], c=color, s=100, label=family)

    ax.set_xlabel('TruthfulQA MC1 Accuracy', fontsize=12)
    ax.set_ylabel('Adversarial Robustness (1 - ASR)', fontsize=12)
    ax.set_title(f'H-E1: Factuality vs Robustness Correlation\n(r={analysis["pearson_r"]:.3f}, p={analysis["p_value"]:.4f})', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Gate metrics plot saved to {out_path}")


def plot_correlation_heatmap(results: Dict, out_path: str = f"{FIGURES_DIR}/correlation_heatmap.png") -> None:
    """Correlation matrix heatmap: MC1, (1-ASR), log(params)."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    mc1 = np.array(results["mc1_acc"])
    robustness = np.array(results["robustness"])
    log_params = np.array(results["log_params"])

    mask = ~(np.isnan(mc1) | np.isnan(robustness) | np.isnan(log_params))
    data = np.column_stack([mc1[mask], robustness[mask], log_params[mask]])

    corr_matrix = np.corrcoef(data.T)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

    labels = ['MC1 Accuracy', 'Robustness (1-ASR)', 'log(Params)']
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                    ha='center', va='center', fontsize=12,
                    color='white' if abs(corr_matrix[i, j]) > 0.5 else 'black')

    plt.colorbar(im, ax=ax, label='Correlation')
    ax.set_title('H-E1: Correlation Matrix', fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Correlation heatmap saved to {out_path}")


def plot_bootstrap_distribution(
    bootstrap_rs: List[float],
    ci: tuple,
    out_path: str = f"{FIGURES_DIR}/bootstrap_distribution.png"
) -> None:
    """Histogram of bootstrap r values with CI markers."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(bootstrap_rs, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='white')

    ax.axvline(x=ci[0], color='red', linestyle='--', linewidth=2, label=f'95% CI lower: {ci[0]:.3f}')
    ax.axvline(x=ci[1], color='red', linestyle='--', linewidth=2, label=f'95% CI upper: {ci[1]:.3f}')
    ax.axvline(x=np.mean(bootstrap_rs), color='black', linewidth=2, label=f'Mean r: {np.mean(bootstrap_rs):.3f}')
    ax.axvline(x=0.3, color='orange', linestyle=':', linewidth=2, label='r=0.3 threshold')
    ax.axvline(x=0.5, color='green', linestyle=':', linewidth=2, label='r=0.5 threshold')

    ax.set_xlabel('Pearson r', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('H-E1: Bootstrap Distribution of Correlation (N=1000)', fontsize=14)
    ax.legend(loc='best', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Bootstrap distribution saved to {out_path}")


def plot_within_family(results: Dict, out_path: str = f"{FIGURES_DIR}/within_family.png") -> None:
    """Separate panels for each model family."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    families = list(set(MODEL_FAMILY.values()))
    n_families = len(families)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, family in enumerate(families):
        ax = axes[idx]

        family_models = [m for m in results["model"] if MODEL_FAMILY.get(m) == family]
        family_idx = [i for i, m in enumerate(results["model"]) if MODEL_FAMILY.get(m) == family]

        mc1 = [results["mc1_acc"][i] for i in family_idx]
        robustness = [results["robustness"][i] for i in family_idx]

        mask = [(not np.isnan(m) and not np.isnan(r)) for m, r in zip(mc1, robustness)]
        mc1_clean = [m for m, valid in zip(mc1, mask) if valid]
        rob_clean = [r for r, valid in zip(robustness, mask) if valid]

        ax.scatter(mc1_clean, rob_clean, c=FAMILY_COLORS.get(family, 'gray'), s=100, alpha=0.8)

        if len(mc1_clean) >= 2:
            r, p = stats.pearsonr(mc1_clean, rob_clean)
            ax.set_title(f'{family.upper()}\n(r={r:.3f}, n={len(mc1_clean)})', fontsize=12)
        else:
            ax.set_title(f'{family.upper()}\n(n={len(mc1_clean)})', fontsize=12)

        ax.set_xlabel('MC1 Accuracy')
        ax.set_ylabel('Robustness')
        ax.grid(True, alpha=0.3)

    for idx in range(n_families, len(axes)):
        axes[idx].axis('off')

    plt.suptitle('H-E1: Within-Family Correlation', fontsize=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Within-family plot saved to {out_path}")


def plot_partial_correlation(results: Dict, out_path: str = f"{FIGURES_DIR}/partial_correlation.png") -> None:
    """Residualized scatter after controlling for scale."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    from sklearn.linear_model import LinearRegression

    mc1 = np.array(results["mc1_acc"])
    robustness = np.array(results["robustness"])
    log_params = np.array(results["log_params"])

    mask = ~(np.isnan(mc1) | np.isnan(robustness) | np.isnan(log_params))
    mc1_clean = mc1[mask]
    rob_clean = robustness[mask]
    log_params_clean = log_params[mask].reshape(-1, 1)

    lr = LinearRegression()
    lr.fit(log_params_clean, mc1_clean)
    resid_mc1 = mc1_clean - lr.predict(log_params_clean)

    lr.fit(log_params_clean, rob_clean)
    resid_rob = rob_clean - lr.predict(log_params_clean)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(resid_mc1, resid_rob, c='steelblue', s=100, alpha=0.8, edgecolors='white')

    r, p = stats.pearsonr(resid_mc1, resid_rob)
    slope, intercept, _, _, _ = stats.linregress(resid_mc1, resid_rob)
    x_line = np.linspace(resid_mc1.min(), resid_mc1.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'Regression (partial r={r:.3f})')

    ax.set_xlabel('MC1 Accuracy (residualized)', fontsize=12)
    ax.set_ylabel('Robustness (residualized)', fontsize=12)
    ax.set_title(f'H-E1: Partial Correlation Controlling for Model Scale\n(partial r={r:.3f}, p={p:.4f})', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Partial correlation plot saved to {out_path}")


def generate_all_figures(results: Dict, analysis: Dict, out_dir: str = FIGURES_DIR) -> List[str]:
    """Generate all required + supporting figures. Returns list of generated file paths."""
    os.makedirs(out_dir, exist_ok=True)
    generated = []

    plot_gate_metrics(results, analysis, f"{out_dir}/gate_metrics.png")
    generated.append(f"{out_dir}/gate_metrics.png")

    plot_correlation_heatmap(results, f"{out_dir}/correlation_heatmap.png")
    generated.append(f"{out_dir}/correlation_heatmap.png")

    if "bootstrap_rs" in analysis and len(analysis["bootstrap_rs"]) > 0:
        plot_bootstrap_distribution(
            analysis["bootstrap_rs"],
            tuple(analysis["ci_95"]),
            f"{out_dir}/bootstrap_distribution.png"
        )
        generated.append(f"{out_dir}/bootstrap_distribution.png")

    plot_within_family(results, f"{out_dir}/within_family.png")
    generated.append(f"{out_dir}/within_family.png")

    plot_partial_correlation(results, f"{out_dir}/partial_correlation.png")
    generated.append(f"{out_dir}/partial_correlation.png")

    print(f"\nGenerated {len(generated)} figures in {out_dir}")
    return generated


def load_results(path: str = RESULTS_PATH) -> Dict:
    """Load results from JSON."""
    with open(path, 'r') as f:
        return json.load(f)


def load_analysis(path: str = ANALYSIS_PATH) -> Dict:
    """Load analysis from JSON."""
    with open(path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    results = load_results()
    analysis = load_analysis()
    generate_all_figures(results, analysis)
