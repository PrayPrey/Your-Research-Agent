"""Evaluation and visualization for h-e1 DTW clustering experiment."""

import numpy as np
from typing import Tuple, Dict, List
import os
from datetime import datetime

from sklearn.metrics import silhouette_score
from scipy.optimize import linear_sum_assignment
from tslearn.clustering import TimeSeriesKMeans

from config import ExperimentConfig


def compute_silhouette(X_flat: np.ndarray, labels: np.ndarray) -> float:
    """Compute silhouette score."""
    return float(silhouette_score(X_flat, labels))


def align_labels(boot_labels: np.ndarray, orig_labels: np.ndarray, k: int) -> np.ndarray:
    """
    Align bootstrap cluster labels to original labels using Hungarian algorithm.
    """
    # Build cost matrix based on overlap
    cost_matrix = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            # Count disagreements
            cost_matrix[i, j] = -np.sum((boot_labels == i) & (orig_labels == j))

    # Solve assignment problem
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Create mapping
    mapping = {row: col for row, col in zip(row_ind, col_ind)}

    # Apply mapping
    aligned = np.array([mapping.get(l, l) for l in boot_labels])
    return aligned


def compute_jaccard_stability(
    X: np.ndarray,
    model: TimeSeriesKMeans,
    config: ExperimentConfig,
) -> float:
    """
    Compute bootstrap Jaccard stability.

    Args:
        X: [N, T, 1] time series data
        model: Fitted DTW model
        config: Experiment configuration

    Returns:
        Mean Jaccard stability score
    """
    original_labels = model.labels_
    n = len(X)
    n_sample = int(n * config.bootstrap_ratio)
    k = model.n_clusters

    jaccard_scores = []

    print(f"Computing Jaccard stability ({config.n_bootstrap} iterations)...")

    for i in range(config.n_bootstrap):
        if (i + 1) % 20 == 0:
            print(f"  Bootstrap iteration {i + 1}/{config.n_bootstrap}")

        # Sample indices without replacement
        idx = np.random.choice(n, size=n_sample, replace=False)
        X_sub = X[idx]

        # Refit model on subsample
        boot_model = TimeSeriesKMeans(
            n_clusters=k,
            metric="dtw",
            max_iter=config.max_iter,
            n_init=config.n_init,
            random_state=None,  # Vary per bootstrap
            verbose=0,
        )
        boot_model.fit(X_sub)
        boot_labels = boot_model.labels_

        # Get original labels for sampled indices
        orig_sub = original_labels[idx]

        # Align labels
        aligned = align_labels(boot_labels, orig_sub, k)

        # Compute per-cluster Jaccard
        jaccards = []
        for c in range(k):
            A = set(np.where(orig_sub == c)[0])
            B = set(np.where(aligned == c)[0])
            if len(A | B) == 0:
                continue
            jaccards.append(len(A & B) / len(A | B))

        if jaccards:
            jaccard_scores.append(np.mean(jaccards))

    mean_jaccard = float(np.mean(jaccard_scores)) if jaccard_scores else 0.0
    print(f"  Mean Jaccard stability: {mean_jaccard:.4f}")

    return mean_jaccard


def verify_mechanism(
    model: TimeSeriesKMeans,
    silhouette: float,
    baseline_silhouette: float,
) -> Tuple[bool, Dict]:
    """
    Verify mechanism activation indicators.
    """
    indicators = {
        "has_cluster_centers": hasattr(model, "cluster_centers_"),
        "n_clusters_valid": model.n_clusters >= 3,
        "silhouette_positive": silhouette > 0,
        "silhouette_vs_base": silhouette >= baseline_silhouette * 0.9,
        "gate_silhouette": silhouette > 0.25,
        "gate_k_valid": 3 <= model.n_clusters <= 8,
    }
    passed = all(indicators.values())
    return passed, indicators


def generate_figures(
    X: np.ndarray,
    labels: np.ndarray,
    silhouette_scores: Dict[int, float],
    model: TimeSeriesKMeans,
    config: ExperimentConfig,
    gate_metrics: Dict,
) -> List[str]:
    """
    Generate and save visualization figures.

    Returns list of generated figure paths.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.manifold import TSNE

    os.makedirs(config.figures_dir, exist_ok=True)
    figure_paths = []

    # 1. Gate metrics bar chart (mandatory)
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics = ['Silhouette Score', 'Jaccard Stability']
    values = [gate_metrics['silhouette'], gate_metrics['jaccard_stability']]
    thresholds = [config.silhouette_threshold, config.jaccard_threshold]

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, values, width, label='Achieved', color='steelblue')
    bars2 = ax.bar(x + width/2, thresholds, width, label='Threshold', color='coral', alpha=0.7)

    ax.set_ylabel('Score')
    ax.set_title('Gate Metrics: Achieved vs Threshold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_ylim(0, 1)

    # Add value labels
    for bar, val in zip(bars1, values):
        ax.annotate(f'{val:.3f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                   ha='center', va='bottom')

    path = os.path.join(config.figures_dir, 'gate_metrics_bar.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    # 2. Silhouette vs k
    fig, ax = plt.subplots(figsize=(10, 6))
    ks = sorted(silhouette_scores.keys())
    scores = [silhouette_scores[k] for k in ks]

    ax.plot(ks, scores, 'o-', markersize=10, linewidth=2)
    ax.axhline(y=config.silhouette_threshold, color='r', linestyle='--', label=f'Threshold ({config.silhouette_threshold})')
    ax.set_xlabel('Number of Clusters (k)')
    ax.set_ylabel('Silhouette Score')
    ax.set_title('Silhouette Score vs Number of Clusters')
    ax.legend()
    ax.set_xticks(ks)
    ax.grid(True, alpha=0.3)

    path = os.path.join(config.figures_dir, 'silhouette_vs_k.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    # 3. Cluster centroids
    fig, ax = plt.subplots(figsize=(12, 6))
    centroids = model.cluster_centers_
    for i in range(centroids.shape[0]):
        ax.plot(centroids[i, :, 0], label=f'Cluster {i}', linewidth=2)

    ax.set_xlabel('Time Step')
    ax.set_ylabel('Normalized Value')
    ax.set_title('Cluster Centroids (DTW Barycenters)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    path = os.path.join(config.figures_dir, 'cluster_centroids.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    # 4. Cluster distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    unique, counts = np.unique(labels, return_counts=True)

    ax.bar(unique, counts, color='steelblue', edgecolor='black')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Number of Datasets')
    ax.set_title('Cluster Size Distribution')
    ax.set_xticks(unique)

    # Add count labels
    for i, (u, c) in enumerate(zip(unique, counts)):
        ax.annotate(str(c), xy=(u, c), ha='center', va='bottom')

    path = os.path.join(config.figures_dir, 'cluster_distribution.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    # 5. t-SNE visualization
    fig, ax = plt.subplots(figsize=(10, 8))

    # Flatten time series for t-SNE
    X_flat = X[:, :, 0]

    # Handle NaN values from padding
    X_flat = np.nan_to_num(X_flat, nan=0.0)

    # Apply t-SNE
    tsne = TSNE(n_components=2, random_state=config.random_state, perplexity=min(30, len(X_flat)-1))
    X_embedded = tsne.fit_transform(X_flat)

    scatter = ax.scatter(X_embedded[:, 0], X_embedded[:, 1], c=labels, cmap='tab10', alpha=0.6)
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    ax.set_title('t-SNE Projection of Clustered Trajectories')
    plt.colorbar(scatter, ax=ax, label='Cluster')

    path = os.path.join(config.figures_dir, 'tsne_projection.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    return figure_paths


def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """
    Write validation report with gate pass/fail determination.
    """
    timestamp = datetime.now().isoformat()

    gate_pass = (
        results['silhouette'] > config.silhouette_threshold and
        config.k_range[0] <= results['optimal_k'] <= config.k_range[1] and
        results['jaccard_stability'] > config.jaccard_threshold
    )

    report = f"""# Validation Report: h-e1

**Hypothesis**: EXISTENCE - DTW clustering of time series data (UCR Archive)
**Generated**: {timestamp}
**Gate Type**: MUST_WORK
**Data Source**: UCR Time Series Classification Archive (real measurement data)

---

## Gate Verdict

**GATE RESULT**: {'PASS' if gate_pass else 'FAIL'}

---

## Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Silhouette Score | {results['silhouette']:.4f} | > {config.silhouette_threshold} | {'PASS' if results['silhouette'] > config.silhouette_threshold else 'FAIL'} |
| Optimal k | {results['optimal_k']} | in [{config.k_range[0]}, {config.k_range[1]}] | {'PASS' if config.k_range[0] <= results['optimal_k'] <= config.k_range[1] else 'FAIL'} |
| Jaccard Stability | {results['jaccard_stability']:.4f} | > {config.jaccard_threshold} | {'PASS' if results['jaccard_stability'] > config.jaccard_threshold else 'FAIL'} |

---

## Secondary Metrics

| Metric | Value |
|--------|-------|
| Baseline Silhouette | {results['baseline_silhouette']:.4f} |
| Baseline k | {results['baseline_k']} |
| Number of Datasets | {results['n_datasets']} |

---

## Silhouette Scores by k

| k | DTW Silhouette | Baseline Silhouette |
|---|----------------|---------------------|
"""

    for k in sorted(results['dtw_silhouette_scores'].keys()):
        dtw_score = results['dtw_silhouette_scores'][k]
        baseline_score = results['baseline_silhouette_scores'].get(k, 'N/A')
        if isinstance(baseline_score, float):
            report += f"| {k} | {dtw_score:.4f} | {baseline_score:.4f} |\n"
        else:
            report += f"| {k} | {dtw_score:.4f} | {baseline_score} |\n"

    report += f"""
---

## Mechanism Verification

| Indicator | Status |
|-----------|--------|
"""

    for indicator, status in results['mechanism_indicators'].items():
        report += f"| {indicator} | {'PASS' if status else 'FAIL'} |\n"

    report += f"""
---

## Figures Generated

"""
    for fig_path in results.get('figure_paths', []):
        report += f"- `{fig_path}`\n"

    report += f"""
---

## Conclusion

"""
    if gate_pass:
        report += """The EXISTENCE hypothesis is **SUPPORTED**. DTW-based clustering reveals
meaningful structure in real UCR time series data with:
- Silhouette score exceeding threshold (clustering quality validated)
- Optimal k within expected range (3-8 distinct clusters exist)
- Bootstrap Jaccard stability above threshold (clusters are reproducible)

**Data Source**: UCR Time Series Classification Archive (real measurement data, not synthetic)

**Next Step**: Proceed to h-m1 (MECHANISM hypothesis - PELT changepoint detection)
"""
    else:
        report += """The EXISTENCE hypothesis is **NOT SUPPORTED**. The clustering structure
does not meet the required criteria. This is a MUST_WORK gate, indicating
fundamental issues with the approach.

**Failed Criteria**:
"""
        if results['silhouette'] <= config.silhouette_threshold:
            report += f"- Silhouette score ({results['silhouette']:.4f}) below threshold ({config.silhouette_threshold})\n"
        if not (config.k_range[0] <= results['optimal_k'] <= config.k_range[1]):
            report += f"- Optimal k ({results['optimal_k']}) outside expected range [{config.k_range[0]}, {config.k_range[1]}]\n"
        if results['jaccard_stability'] <= config.jaccard_threshold:
            report += f"- Jaccard stability ({results['jaccard_stability']:.4f}) below threshold ({config.jaccard_threshold})\n"

    # Write report
    os.makedirs(os.path.dirname(config.output_path), exist_ok=True)
    with open(config.output_path, 'w') as f:
        f.write(report)

    print(f"Validation report written to: {config.output_path}")

    return 'PASS' if gate_pass else 'FAIL'
