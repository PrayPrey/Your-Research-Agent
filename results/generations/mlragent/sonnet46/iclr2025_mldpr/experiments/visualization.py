"""
Visualization module for the Dynamic Benchmark Renewal Framework experiments.
Generates all figures for analysis and results.md.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path


DOMAIN_COLORS = {
    'image_classification': '#2196F3',
    'nlp': '#4CAF50',
    'tabular': '#FF9800'
}

DOMAIN_LABELS = {
    'image_classification': 'Image Classification',
    'nlp': 'NLP',
    'tabular': 'Tabular'
}

METHOD_COLORS = {
    'DBRF (Ours)': '#E74C3C',
    'Static Baseline': '#95A5A6',
    'Random Renewal': '#3498DB',
    'Adversarial': '#F39C12',
}


def create_all_figures(aggregated_results, config, output_dir):
    """Create all visualization figures."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nGenerating figures...")

    # 1. Performance trajectories with saturation detection
    plot_performance_trajectories(aggregated_results, output_dir)
    print("  [1/6] Performance trajectories figure saved.")

    # 2. Overfitting reduction comparison (DBRF vs baselines)
    plot_overfitting_comparison(aggregated_results, output_dir)
    print("  [2/6] Overfitting comparison figure saved.")

    # 3. KL divergence across renewal cycles
    plot_kl_divergence(aggregated_results, output_dir)
    print("  [3/6] KL divergence figure saved.")

    # 4. Detection metrics (precision, recall, F1)
    plot_detection_metrics(aggregated_results, output_dir)
    print("  [4/6] Detection metrics figure saved.")

    # 5. Cross-version calibration error and rank correlation
    plot_anchoring_metrics(aggregated_results, output_dir)
    print("  [5/6] Anchoring metrics figure saved.")

    # 6. Summary radar / heatmap chart
    plot_summary_comparison(aggregated_results, output_dir)
    print("  [6/6] Summary comparison figure saved.")

    print(f"All figures saved to {output_dir}")


def plot_performance_trajectories(aggregated_results, output_dir):
    """
    Plot benchmark vs shadow performance trajectories across domains.
    Shows saturation detection points.
    """
    domains = list(aggregated_results['domains'].keys())
    n_domains = len(domains)

    fig, axes = plt.subplots(1, n_domains, figsize=(6 * n_domains, 5))
    if n_domains == 1:
        axes = [axes]

    for ax, domain in zip(axes, domains):
        domain_data = aggregated_results['domains'][domain]
        detection = domain_data['detection_metrics']

        n_gen = len(detection['benchmark_scores_trajectory'])
        generations = np.arange(n_gen)

        bench_scores = np.array(detection['benchmark_scores_trajectory'])
        shadow_scores = np.array(detection['shadow_scores_trajectory'])
        fitted = np.array(detection['fitted_trajectory'])
        sat_detected = np.array(detection['saturation_detected_per_gen'])

        # Plot trajectories
        ax.plot(generations, bench_scores, 'b-o', markersize=4, label='Benchmark Score', linewidth=2)
        ax.plot(generations, shadow_scores, 'g-s', markersize=4, label='Shadow Set Score', linewidth=2)
        ax.plot(generations, fitted, 'b--', alpha=0.5, label='Fitted Growth Curve', linewidth=1.5)

        # Fill region between benchmark and shadow (overfitting gap)
        ax.fill_between(generations, shadow_scores, bench_scores,
                        alpha=0.15, color='red', label='Overfitting Gap')

        # Mark saturation detection
        sat_start = int(n_gen * 0.6)
        ax.axvline(x=sat_start, color='orange', linestyle='--', linewidth=1.5,
                   label='Saturation Threshold')

        # Highlight detected saturation points
        sat_gens = generations[sat_detected]
        if len(sat_gens) > 0:
            ax.scatter(sat_gens, bench_scores[sat_detected], color='red',
                       zorder=5, marker='x', s=80, linewidths=2, label='Detected Saturation')

        ax.set_xlabel('Model Generation', fontsize=12)
        ax.set_ylabel('Performance Score', fontsize=12)
        ax.set_title(f'{DOMAIN_LABELS[domain]}\nBenchmark vs Shadow Performance', fontsize=13, fontweight='bold')
        ax.legend(fontsize=9, loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0.45, 1.02)

    plt.suptitle('Performance Trajectory Analysis Across Domains', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_trajectories.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_overfitting_comparison(aggregated_results, output_dir):
    """
    Compare overfitting reduction across methods and domains.
    Bar chart with error bars.
    """
    domains = list(aggregated_results['domains'].keys())
    domain_labels = [DOMAIN_LABELS[d] for d in domains]

    methods = ['DBRF (Ours)', 'Static Baseline', 'Random Renewal', 'Adversarial']

    # Collect data for each method and domain
    method_data = {method: [] for method in methods}

    for domain in domains:
        domain_data = aggregated_results['domains'][domain]

        # DBRF: average over evolution cycles
        dbrf_reduction = domain_data['dbrf']['overfitting_reduction']
        method_data['DBRF (Ours)'].append(dbrf_reduction)

        # Baselines
        method_data['Static Baseline'].append(
            domain_data['baselines']['static']['overfitting_reduction']
        )
        method_data['Random Renewal'].append(
            domain_data['baselines']['random_renewal']['overfitting_reduction']
        )
        method_data['Adversarial'].append(
            domain_data['baselines']['adversarial']['overfitting_reduction']
        )

    fig, ax = plt.subplots(figsize=(10, 6))

    n_domains = len(domains)
    n_methods = len(methods)
    bar_width = 0.18
    x = np.arange(n_domains)

    for i, method in enumerate(methods):
        values = method_data[method]
        bars = ax.bar(
            x + i * bar_width - (n_methods - 1) * bar_width / 2,
            values, bar_width,
            label=method,
            color=METHOD_COLORS[method],
            alpha=0.85,
            edgecolor='white',
            linewidth=0.5
        )
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.005,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(domain_labels, fontsize=12)
    ax.set_ylabel('Overfitting Reduction', fontsize=12)
    ax.set_title('Overfitting Reduction by Method and Domain\n(Higher is Better)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 0.85)
    ax.axhline(y=0.0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_dir / 'overfitting_reduction_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_kl_divergence(aggregated_results, output_dir):
    """
    Plot KL divergence across renewal cycles for each domain and baseline.
    """
    domains = list(aggregated_results['domains'].keys())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: KL divergence per cycle per domain (DBRF)
    ax = axes[0]
    for domain in domains:
        domain_data = aggregated_results['domains'][domain]
        evolution_results = domain_data['evolution_results']
        cycles = [r['cycle'] for r in evolution_results]
        kl_values = [r['kl_divergence'] for r in evolution_results]

        ax.plot(cycles, kl_values, 'o-', label=DOMAIN_LABELS[domain],
                color=DOMAIN_COLORS[domain], linewidth=2, markersize=8)

    ax.axhline(y=aggregated_results['config']['kl_epsilon'],
               color='red', linestyle='--', linewidth=1.5, label=f'Tolerance ε={aggregated_results["config"]["kl_epsilon"]}')
    ax.set_xlabel('Renewal Cycle', fontsize=12)
    ax.set_ylabel('KL Divergence (JS)', fontsize=12)
    ax.set_title('Distributional Fidelity\nKL Divergence per Renewal Cycle (DBRF)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks([1, 2, 3])

    # Right: KL divergence comparison between DBRF and baselines (box plot style)
    ax = axes[1]

    # Collect KL values for each method
    dbrf_kl = []
    random_kl = []
    adversarial_kl = []

    for domain in domains:
        domain_data = aggregated_results['domains'][domain]
        for cycle_data in domain_data['evolution_results']:
            dbrf_kl.append(cycle_data['kl_divergence'])

        random_baseline = domain_data['baselines'].get('random_renewal', {})
        random_kl.extend(random_baseline.get('kl_divergences', []))

        adversarial_baseline = domain_data['baselines'].get('adversarial', {})
        adversarial_kl.extend(adversarial_baseline.get('kl_divergences', []))

    method_kl_data = {
        'DBRF\n(Ours)': dbrf_kl,
        'Random\nRenewal': random_kl,
        'Adversarial': adversarial_kl,
    }

    positions = np.arange(len(method_kl_data))
    for pos, (method, kl_vals) in zip(positions, method_kl_data.items()):
        bp = ax.boxplot(kl_vals, positions=[pos], widths=0.5, patch_artist=True)
        color = METHOD_COLORS.get(method.replace('\n', ' '), '#999999')
        bp['boxes'][0].set_facecolor(color)
        bp['boxes'][0].set_alpha(0.7)

        # Add mean marker
        ax.scatter([pos], [np.mean(kl_vals)], color='white', zorder=5, s=80, marker='D')

    ax.axhline(y=aggregated_results['config']['kl_epsilon'],
               color='red', linestyle='--', linewidth=1.5, label=f'Tolerance ε={aggregated_results["config"]["kl_epsilon"]}')
    ax.set_xticks(positions)
    ax.set_xticklabels(list(method_kl_data.keys()), fontsize=11)
    ax.set_ylabel('KL Divergence (JS)', fontsize=12)
    ax.set_title('KL Divergence Comparison\nAcross Renewal Methods', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'kl_divergence.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_detection_metrics(aggregated_results, output_dir):
    """
    Plot contamination detection metrics (precision, recall, F1, accuracy) per domain.
    """
    domains = list(aggregated_results['domains'].keys())
    domain_labels = [DOMAIN_LABELS[d] for d in domains]

    metrics = ['precision', 'recall', 'f1', 'accuracy']
    metric_labels = ['Precision', 'Recall', 'F1 Score', 'Accuracy']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Bar chart of metrics per domain
    ax = axes[0]
    n_domains = len(domains)
    n_metrics = len(metrics)
    bar_width = 0.18
    x = np.arange(n_metrics)

    for i, (domain, label) in enumerate(zip(domains, domain_labels)):
        detection = aggregated_results['domains'][domain]['detection_metrics']
        values = [detection[m] for m in metrics]
        bars = ax.bar(
            x + i * bar_width - (n_domains - 1) * bar_width / 2,
            values, bar_width,
            label=label,
            color=DOMAIN_COLORS[domain],
            alpha=0.85,
            edgecolor='white'
        )

    ax.axhline(y=0.85, color='red', linestyle='--', linewidth=1.5, label='Target (0.85)')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=11)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Contamination Detection Metrics\nPer Domain', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.05)

    # Right: Confusion matrix-like heatmap (aggregated)
    ax = axes[1]

    all_tp = sum(aggregated_results['domains'][d]['detection_metrics']['tp'] for d in domains)
    all_fp = sum(aggregated_results['domains'][d]['detection_metrics']['fp'] for d in domains)
    all_fn = sum(aggregated_results['domains'][d]['detection_metrics']['fn'] for d in domains)
    all_tn = sum(aggregated_results['domains'][d]['detection_metrics']['tn'] for d in domains)

    conf_matrix = np.array([[all_tp, all_fn], [all_fp, all_tn]])
    total = conf_matrix.sum()

    im = ax.imshow(conf_matrix / total, cmap='Blues', vmin=0, vmax=1)

    labels_mat = [['True Pos', 'False Neg'], ['False Pos', 'True Neg']]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{labels_mat[i][j]}\n{conf_matrix[i, j]}\n({100*conf_matrix[i,j]/total:.1f}%)',
                    ha='center', va='center', fontsize=11,
                    color='white' if conf_matrix[i, j] / total > 0.4 else 'black',
                    fontweight='bold')

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Predicted Saturated', 'Predicted Not Sat.'], fontsize=10)
    ax.set_yticklabels(['Actually Saturated', 'Actually Not Sat.'], fontsize=10)
    ax.set_title('Aggregated Detection Confusion Matrix\n(All Domains)', fontsize=13, fontweight='bold')
    plt.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    plt.savefig(output_dir / 'detection_metrics.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_anchoring_metrics(aggregated_results, output_dir):
    """
    Plot cross-version anchoring: calibration error and rank correlation per domain.
    """
    domains = list(aggregated_results['domains'].keys())
    domain_labels = [DOMAIN_LABELS[d] for d in domains]

    calibration_errors = [aggregated_results['domains'][d]['anchoring_metrics']['calibration_error'] for d in domains]
    rank_correlations = [aggregated_results['domains'][d]['anchoring_metrics']['rank_correlation'] for d in domains]
    anchor_coverages = [aggregated_results['domains'][d]['anchoring_metrics']['anchor_coverage'] for d in domains]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Left: Calibration error per domain
    ax = axes[0]
    bars = ax.bar(domain_labels, calibration_errors,
                  color=[DOMAIN_COLORS[d] for d in domains], alpha=0.85, edgecolor='white')
    ax.axhline(y=0.015, color='red', linestyle='--', linewidth=1.5, label='Target (<0.015)')
    for bar, val in zip(bars, calibration_errors):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0003,
                f'{val:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Mean Absolute Calibration Error', fontsize=11)
    ax.set_title('Cross-Version Calibration Error\n(Lower is Better)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Middle: Rank correlation per domain
    ax = axes[1]
    bars = ax.bar(domain_labels, rank_correlations,
                  color=[DOMAIN_COLORS[d] for d in domains], alpha=0.85, edgecolor='white')
    ax.axhline(y=0.9, color='green', linestyle='--', linewidth=1.5, label='Target (>0.90)')
    for bar, val in zip(bars, rank_correlations):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Spearman Rank Correlation', fontsize=11)
    ax.set_title('Cross-Version Rank Correlation\n(Higher is Better)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.05)

    # Right: Anchor set coverage
    ax = axes[2]
    bars = ax.bar(domain_labels, anchor_coverages,
                  color=[DOMAIN_COLORS[d] for d in domains], alpha=0.85, edgecolor='white')
    ax.axhline(y=0.9, color='green', linestyle='--', linewidth=1.5, label='Target (>0.90)')
    for bar, val in zip(bars, anchor_coverages):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('Coverage of Difficulty Range', fontsize=11)
    ax.set_title('Anchor Set Coverage\n(Difficulty Distribution)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.05)

    plt.suptitle('Cross-Version Performance Anchoring Metrics', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'anchoring_metrics.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_summary_comparison(aggregated_results, output_dir):
    """
    Create a comprehensive summary comparison figure showing all methods and metrics.
    """
    domains = list(aggregated_results['domains'].keys())
    domain_labels = [DOMAIN_LABELS[d] for d in domains]

    # Collect all metrics for all methods
    methods = ['DBRF (Ours)', 'Static Baseline', 'Random Renewal', 'Adversarial']
    metric_names = ['Overfitting\nReduction', 'KL Fidelity\n(1-KL)', 'Rank\nCorrelation', 'Detection\nF1']

    # Build metric matrix [methods x metrics] averaged across domains
    metric_matrix = np.zeros((len(methods), len(metric_names)))

    for dom_i, domain in enumerate(domains):
        domain_data = aggregated_results['domains'][domain]

        # DBRF metrics
        dbrf_data = domain_data['dbrf']
        detection = domain_data['detection_metrics']
        anchoring = domain_data['anchoring_metrics']
        evolution = domain_data['evolution_results']

        dbrf_kl = float(np.mean([r['kl_divergence'] for r in evolution]))

        metric_matrix[0, 0] += dbrf_data['overfitting_reduction'] / len(domains)
        metric_matrix[0, 1] += max(0, 1 - dbrf_kl * 10) / len(domains)  # Normalize
        metric_matrix[0, 2] += anchoring['rank_correlation'] / len(domains)
        metric_matrix[0, 3] += detection['f1'] / len(domains)

        # Static baseline
        static = domain_data['baselines']['static']
        metric_matrix[1, 0] += static['overfitting_reduction'] / len(domains)
        metric_matrix[1, 1] += 1.0 / len(domains)  # No renewal, no KL
        metric_matrix[1, 2] += static.get('rank_stability', 0.55) / len(domains)
        metric_matrix[1, 3] += 0.0 / len(domains)  # Static has no detection

        # Random renewal
        random_r = domain_data['baselines']['random_renewal']
        random_kl = float(np.mean(random_r.get('kl_divergences', [0.15])))
        metric_matrix[2, 0] += random_r['overfitting_reduction'] / len(domains)
        metric_matrix[2, 1] += max(0, 1 - random_kl * 10) / len(domains)
        metric_matrix[2, 2] += random_r.get('rank_stability', 0.65) / len(domains)
        metric_matrix[2, 3] += 0.0 / len(domains)  # No systematic detection

        # Adversarial
        adv = domain_data['baselines']['adversarial']
        adv_kl = float(np.mean(adv.get('kl_divergences', [0.07])))
        metric_matrix[3, 0] += adv['overfitting_reduction'] / len(domains)
        metric_matrix[3, 1] += max(0, 1 - adv_kl * 10) / len(domains)
        metric_matrix[3, 2] += adv.get('rank_stability', 0.75) / len(domains)
        metric_matrix[3, 3] += 0.0 / len(domains)  # No IRT calibration

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left: Grouped bar chart
    ax = axes[0]
    n_metrics = len(metric_names)
    n_methods = len(methods)
    bar_width = 0.18
    x = np.arange(n_metrics)

    for i, method in enumerate(methods):
        bars = ax.bar(
            x + i * bar_width - (n_methods - 1) * bar_width / 2,
            metric_matrix[i],
            bar_width,
            label=method,
            color=METHOD_COLORS[method],
            alpha=0.85,
            edgecolor='white'
        )

    ax.set_xticks(x)
    ax.set_xticklabels(metric_names, fontsize=11)
    ax.set_ylabel('Score (normalized)', fontsize=12)
    ax.set_title('Comprehensive Method Comparison\n(Average Across Domains)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.15)

    # Right: Heatmap of metrics per domain for DBRF
    ax = axes[1]

    # Build per-domain DBRF metrics
    domain_metric_matrix = np.zeros((len(domains), 4))
    for dom_i, domain in enumerate(domains):
        domain_data = aggregated_results['domains'][domain]
        dbrf_data = domain_data['dbrf']
        detection = domain_data['detection_metrics']
        anchoring = domain_data['anchoring_metrics']
        evolution = domain_data['evolution_results']
        dbrf_kl = float(np.mean([r['kl_divergence'] for r in evolution]))

        domain_metric_matrix[dom_i, 0] = dbrf_data['overfitting_reduction']
        domain_metric_matrix[dom_i, 1] = max(0, 1 - dbrf_kl * 10)
        domain_metric_matrix[dom_i, 2] = anchoring['rank_correlation']
        domain_metric_matrix[dom_i, 3] = detection['f1']

    im = ax.imshow(domain_metric_matrix, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')

    for i in range(len(domains)):
        for j in range(4):
            ax.text(j, i, f'{domain_metric_matrix[i, j]:.2f}',
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='black' if 0.3 < domain_metric_matrix[i, j] < 0.7 else 'white')

    ax.set_xticks(range(4))
    ax.set_xticklabels(['Overfit\nReduc.', 'KL\nFidelity', 'Rank\nCorr.', 'Detection\nF1'], fontsize=11)
    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels(domain_labels, fontsize=11)
    ax.set_title('DBRF Performance Heatmap\nPer Domain and Metric', fontsize=13, fontweight='bold')
    plt.colorbar(im, ax=ax, shrink=0.8)

    plt.suptitle('Dynamic Benchmark Renewal Framework - Summary Results', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'summary_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
