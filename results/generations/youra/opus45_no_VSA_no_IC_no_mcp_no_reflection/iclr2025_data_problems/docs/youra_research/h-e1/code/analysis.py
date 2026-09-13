"""Statistical analysis and visualization for h-e1."""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from config import CONFIG


def descriptive_stats(scores: dict[str, float]) -> dict:
    """Compute mean, std, min, max of domain scores."""
    values = list(scores.values())
    return {
        "mean": np.mean(values),
        "std": np.std(values),
        "min": np.min(values),
        "max": np.max(values),
    }


def anova_test(per_sample_scores: list[np.ndarray]) -> tuple[float, float]:
    """Run one-way ANOVA across domain groups.

    Args:
        per_sample_scores: list of arrays, one per domain, containing per-sample similarities.

    Returns:
        (F-statistic, p-value)
    """
    f_stat, p_val = stats.f_oneway(*per_sample_scores)
    return float(f_stat), float(p_val)


def reproducibility_check(runs: list[dict[str, float]]) -> float:
    """Compute variance of domain scores across runs.

    Returns max variance across any domain.
    """
    domains = runs[0].keys()
    variances = []

    for domain in domains:
        domain_scores = [run[domain] for run in runs]
        variances.append(np.var(domain_scores))

    return float(np.max(variances))


def plot_domain_bar(scores: dict[str, float], out_path: str) -> None:
    """Generate bar chart of domain similarity scores."""
    plt.figure(figsize=(10, 6))

    domains = list(scores.keys())
    values = list(scores.values())

    bars = plt.bar(domains, values, color='steelblue', edgecolor='black')

    plt.xlabel('Domain', fontsize=12)
    plt.ylabel('Mean Similarity to MMLU', fontsize=12)
    plt.title('E5-large Domain-Task Similarity Scores', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, max(values) * 1.1)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def write_report(scores: dict[str, float], stats_dict: dict,
                 anova_result: tuple[float, float],
                 repro_var: float, pass_fail: bool,
                 baseline_scores: dict[str, float],
                 out_path: str) -> None:
    """Generate markdown analysis report."""
    lines = [
        "# h-e1 Experiment Results",
        "",
        "## Summary",
        "",
        f"**Gate Verdict:** {'PASS' if pass_fail else 'FAIL'}",
        "",
        "## Domain Similarity Scores",
        "",
        "| Domain | Score |",
        "|--------|-------|",
    ]

    for domain, score in sorted(scores.items()):
        lines.append(f"| {domain} | {score:.4f} |")

    lines.extend([
        "",
        "## Descriptive Statistics",
        "",
        f"- Mean: {stats_dict['mean']:.4f}",
        f"- Std: {stats_dict['std']:.4f}",
        f"- Min: {stats_dict['min']:.4f}",
        f"- Max: {stats_dict['max']:.4f}",
        "",
        "## Success Criteria Evaluation",
        "",
        f"1. **Non-trivial variance (std > {CONFIG['min_cross_domain_std']}):** "
        f"{'PASS' if stats_dict['std'] > CONFIG['min_cross_domain_std'] else 'FAIL'} "
        f"(std = {stats_dict['std']:.4f})",
        "",
        f"2. **ANOVA significance (p < {CONFIG['anova_p_threshold']}):** "
        f"{'PASS' if anova_result[1] < CONFIG['anova_p_threshold'] else 'FAIL'} "
        f"(F = {anova_result[0]:.2f}, p = {anova_result[1]:.4e})",
        "",
        f"3. **Reproducibility (var < {CONFIG['max_reproducibility_variance']}):** "
        f"{'PASS' if repro_var < CONFIG['max_reproducibility_variance'] else 'FAIL'} "
        f"(variance = {repro_var:.6f})",
        "",
        "## Random Baseline Comparison",
        "",
        "| Domain | E5 Score | Random Score |",
        "|--------|----------|--------------|",
    ])

    for domain in sorted(scores.keys()):
        lines.append(f"| {domain} | {scores[domain]:.4f} | {baseline_scores.get(domain, 0):.4f} |")

    baseline_std = np.std(list(baseline_scores.values()))
    lines.extend([
        "",
        f"Random baseline std: {baseline_std:.4f} (expect near-zero variance for random embeddings)",
        "",
        "## Conclusion",
        "",
    ])

    if pass_fail:
        lines.append("E5-large embeddings successfully produce non-trivial, statistically significant, "
                    "and reproducible variance in domain-task similarity scores. The hypothesis h-e1 is **VALIDATED**.")
    else:
        lines.append("E5-large embeddings did not meet all success criteria. The hypothesis h-e1 is **NOT VALIDATED**.")

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines))
