"""Evaluation functions for h-m2 Shape Descriptor experiment.

Implements variance analysis, gate metrics, visualization, and report generation.
"""

import numpy as np
import os
from typing import Dict, List, Tuple
from datetime import datetime
from sklearn.metrics import pairwise_distances

from config import ExperimentConfig


def compute_inter_cluster_variance(
    descriptor_matrix: np.ndarray,
    descriptor_names: List[str]
) -> Dict[str, float]:
    """
    Variance of each descriptor across k centroids.

    Args:
        descriptor_matrix: (k, D) where D is number of descriptors

    Returns:
        dict: descriptor_name -> variance scalar
    """
    inter_variance = {}
    for j, name in enumerate(descriptor_names):
        inter_variance[name] = float(np.var(descriptor_matrix[:, j]))
    return inter_variance


def normalize_series(series: np.ndarray) -> np.ndarray:
    """
    Normalize a single series using log-transform + z-score.
    Matches the preprocessing applied to centroids.
    """
    # Remove trailing zeros (padding)
    nonzero_idx = np.where(series != 0)[0]
    if len(nonzero_idx) > 0:
        series = series[:nonzero_idx[-1] + 1]

    # Log transform (shift to positive first)
    min_val = np.min(series)
    if min_val <= 0:
        series = series - min_val + 1
    series = np.log1p(series)

    # Z-score normalize
    mean_val = np.mean(series)
    std_val = np.std(series)
    if std_val > 1e-10:
        series = (series - mean_val) / std_val

    return series


def compute_intra_cluster_variance(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    analyzer,  # ShapeDescriptorAnalyzer
    descriptor_names: List[str],
    config: ExperimentConfig
) -> Dict[str, float]:
    """
    Bootstrap intra-cluster descriptor variance, averaged across clusters.

    For each cluster:
    1. Get member series
    2. Bootstrap sample n_bootstrap times
    3. Compute descriptors for each sample (after normalization)
    4. Compute variance of descriptors within bootstrap

    Returns:
        dict: descriptor_name -> mean intra-cluster variance
    """
    from data import get_cluster_members

    rng = np.random.RandomState(config.bootstrap_seed)

    k = config.n_clusters

    # Accumulate variance per cluster per descriptor
    cluster_variances = {name: [] for name in descriptor_names}

    for c in range(k):
        members = get_cluster_members(all_series, cluster_labels, c)

        if len(members) < 2:
            # Not enough members for variance
            for name in descriptor_names:
                cluster_variances[name].append(0.0)
            continue

        # Normalize all members first (same preprocessing as centroids)
        normalized_members = [normalize_series(m.copy()) for m in members]

        # Bootstrap sampling
        bootstrap_descriptors = {name: [] for name in descriptor_names}

        for _ in range(config.n_bootstrap):
            # Sample with replacement
            sample_indices = rng.choice(len(normalized_members), size=len(normalized_members), replace=True)
            sample_series = [normalized_members[i] for i in sample_indices]

            # Compute descriptors for each sampled series
            for series in sample_series:
                desc = analyzer.compute_descriptors(series)
                for name in descriptor_names:
                    bootstrap_descriptors[name].append(desc[name])

        # Compute variance within this cluster's bootstrap samples
        for name in descriptor_names:
            var_val = np.var(bootstrap_descriptors[name])
            cluster_variances[name].append(var_val)

    # Average across clusters
    intra_variance = {}
    for name in descriptor_names:
        intra_variance[name] = float(np.mean(cluster_variances[name]))

    return intra_variance


def compute_variance_ratios(
    inter_variance: Dict[str, float],
    intra_variance: Dict[str, float],
    epsilon: float = 1e-8
) -> Dict[str, float]:
    """
    Inter/intra ratio per descriptor.

    Returns:
        dict: descriptor_name -> ratio scalar
    """
    ratios = {}
    for name in inter_variance:
        inter_val = inter_variance[name]
        intra_val = intra_variance.get(name, epsilon)
        ratios[name] = inter_val / (intra_val + epsilon)
    return ratios


def compute_gate_metrics(
    variance_ratios: Dict[str, float],
    descriptor_matrix: np.ndarray,
    config: ExperimentConfig
) -> Dict:
    """
    Evaluate gate: variance_ratio > 2.0 on >= 2 descriptors.

    Also check for distinct descriptor profiles (no two clusters identical).

    Returns:
        dict with gate_pass, n_passing_descriptors, passing_descriptors,
             distinct_profiles, pairwise_distances
    """
    # Check variance ratio threshold
    passing_descriptors = []
    for name, ratio in variance_ratios.items():
        if ratio > config.variance_ratio_threshold:
            passing_descriptors.append(name)

    n_passing = len(passing_descriptors)
    ratio_gate_pass = n_passing >= config.min_descriptors_passing

    # Check distinct profiles (pairwise distances)
    dist_matrix = pairwise_distances(descriptor_matrix)
    # Get off-diagonal elements
    k = descriptor_matrix.shape[0]
    off_diagonal = []
    for i in range(k):
        for j in range(i + 1, k):
            off_diagonal.append(dist_matrix[i, j])

    min_distance = min(off_diagonal) if off_diagonal else 0.0
    distinct_profiles = min_distance > 1e-6  # Not all identical

    # Overall gate pass
    gate_pass = ratio_gate_pass and distinct_profiles

    return {
        "gate_pass": gate_pass,
        "n_passing_descriptors": n_passing,
        "passing_descriptors": passing_descriptors,
        "ratio_gate_pass": ratio_gate_pass,
        "distinct_profiles": distinct_profiles,
        "min_pairwise_distance": float(min_distance),
        "pairwise_distance_matrix": dist_matrix.tolist()
    }


def generate_figures(
    centroids: np.ndarray,
    descriptor_matrix: np.ndarray,
    descriptor_names: List[str],
    variance_ratios: Dict[str, float],
    baseline_matrix: np.ndarray,
    baseline_names: List[str],
    config: ExperimentConfig
) -> List[str]:
    """
    Generate and save all figures.

    Figures:
    1. gate_metrics_bar.png - variance ratio per descriptor with 2.0 threshold
    2. centroid_overlay.png - all k centroids on same axes
    3. descriptor_radar.png - radar chart per cluster
    4. descriptor_scatter.png - 2D PCA of 4D descriptor space
    5. distance_heatmap.png - pairwise descriptor distances

    Returns:
        List of saved figure paths
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.decomposition import PCA

    os.makedirs(config.figures_dir, exist_ok=True)
    figure_paths = []

    k = centroids.shape[0]
    colors = plt.cm.tab10(np.linspace(0, 1, k))

    # 1. Gate Metrics Bar Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(variance_ratios.keys())
    values = [variance_ratios[n] for n in names]
    bars = ax.bar(names, values, color='steelblue', alpha=0.7)
    ax.axhline(y=config.variance_ratio_threshold, color='red', linestyle='--',
               label=f'Threshold = {config.variance_ratio_threshold}')
    ax.set_ylabel('Variance Ratio (Inter/Intra)')
    ax.set_xlabel('Shape Descriptor')
    ax.set_title('h-m2 Gate Metrics: Shape Descriptor Variance Ratios')
    ax.legend()

    # Color bars above threshold
    for bar, val in zip(bars, values):
        if val > config.variance_ratio_threshold:
            bar.set_color('green')

    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'gate_metrics_bar.png')
    plt.savefig(path, dpi=300)
    plt.close()
    figure_paths.append(path)

    # 2. Centroid Overlay Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(k):
        centroid = centroids[i]
        # Remove NaN/zero padding for plotting
        centroid = np.nan_to_num(centroid, nan=0.0)
        ax.plot(centroid, label=f'Cluster {i}', color=colors[i], linewidth=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Normalized Value')
    ax.set_title('Cluster Centroids Overlay')
    ax.legend()
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'centroid_overlay.png')
    plt.savefig(path, dpi=300)
    plt.close()
    figure_paths.append(path)

    # 3. Descriptor Radar Chart
    from math import pi

    # Normalize descriptor matrix for radar
    from model import ShapeDescriptorAnalyzer
    analyzer = ShapeDescriptorAnalyzer(config)
    normalized = analyzer.normalize_descriptors(descriptor_matrix)

    fig, axes = plt.subplots(1, k, figsize=(4 * k, 4), subplot_kw=dict(polar=True))
    if k == 1:
        axes = [axes]

    angles = [n / float(len(descriptor_names)) * 2 * pi for n in range(len(descriptor_names))]
    angles += angles[:1]  # Close the polygon

    for i, ax in enumerate(axes):
        values = normalized[i].tolist()
        values += values[:1]  # Close the polygon
        ax.plot(angles, values, 'o-', linewidth=2, color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(descriptor_names, size=8)
        ax.set_title(f'Cluster {i}', size=12)

    plt.suptitle('Shape Descriptor Profiles (Normalized)', y=1.02)
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'descriptor_radar.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    figure_paths.append(path)

    # 4. Descriptor Scatter (PCA)
    fig, ax = plt.subplots(figsize=(8, 6))
    if descriptor_matrix.shape[1] >= 2:
        if descriptor_matrix.shape[1] > 2:
            pca = PCA(n_components=2)
            coords = pca.fit_transform(descriptor_matrix)
            ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var)')
            ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} var)')
        else:
            coords = descriptor_matrix
            ax.set_xlabel(descriptor_names[0])
            ax.set_ylabel(descriptor_names[1])

        for i in range(k):
            ax.scatter(coords[i, 0], coords[i, 1], s=200, c=[colors[i]],
                      label=f'Cluster {i}', edgecolors='black', linewidth=2)
        ax.legend()
        ax.set_title('Cluster Centroids in Descriptor Space (PCA)')
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'descriptor_scatter.png')
    plt.savefig(path, dpi=300)
    plt.close()
    figure_paths.append(path)

    # 5. Distance Heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    dist_matrix = pairwise_distances(descriptor_matrix)
    sns.heatmap(dist_matrix, annot=True, fmt='.3f', cmap='YlOrRd',
                xticklabels=[f'C{i}' for i in range(k)],
                yticklabels=[f'C{i}' for i in range(k)],
                ax=ax)
    ax.set_title('Pairwise Descriptor Distances Between Clusters')
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'distance_heatmap.png')
    plt.savefig(path, dpi=300)
    plt.close()
    figure_paths.append(path)

    print(f"Generated {len(figure_paths)} figures")
    return figure_paths


def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """
    Write 04_validation.md with gate pass/fail.

    Returns:
        'PASS' or 'FAIL'
    """
    gate_pass = results['gate_pass']
    gate_result = 'PASS' if gate_pass else 'FAIL'

    report = f"""# Validation Report: h-m2

**Hypothesis**: MECHANISM - Shape descriptor differentiation across cluster centroids
**Generated**: {datetime.now().isoformat()}
**Gate Type**: SHOULD_WORK
**Data Source**: Reused from h-e1 (HuggingFace Hub time series)

---

## Gate Verdict

**GATE RESULT**: {gate_result}

---

## Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Passing Descriptors | {results['n_passing_descriptors']} | >= {config.min_descriptors_passing} | {'PASS' if results['ratio_gate_pass'] else 'FAIL'} |
| Distinct Profiles | {results['distinct_profiles']} | True | {'PASS' if results['distinct_profiles'] else 'FAIL'} |
| Min Pairwise Distance | {results['min_pairwise_distance']:.4f} | > 0 | {'PASS' if results['min_pairwise_distance'] > 0 else 'FAIL'} |

---

## Variance Ratios by Descriptor

| Descriptor | Inter-Cluster Var | Intra-Cluster Var | Ratio | Threshold | Status |
|------------|-------------------|-------------------|-------|-----------|--------|
"""

    for name in results['descriptor_names']:
        inter_val = results['inter_variance'][name]
        intra_val = results['intra_variance'][name]
        ratio = results['variance_ratios'][name]
        status = 'PASS' if ratio > config.variance_ratio_threshold else 'FAIL'
        report += f"| {name} | {inter_val:.6f} | {intra_val:.6f} | {ratio:.4f} | > {config.variance_ratio_threshold} | {status} |\n"

    report += f"""
---

## Descriptor Matrix (per Cluster)

| Cluster | {' | '.join(results['descriptor_names'])} |
|---------|{'|'.join(['--------' for _ in results['descriptor_names']])}|
"""

    for i, row in enumerate(results['descriptor_matrix']):
        row_str = ' | '.join([f'{v:.4f}' for v in row])
        report += f"| Cluster {i} | {row_str} |\n"

    report += f"""
---

## Cluster Statistics

| Statistic | Value |
|-----------|-------|
| Number of Clusters (k) | {results['n_clusters']} |
| Number of Series | {results['n_series']} |
| Centroids Shape | {results['centroids_shape']} |

---

## Mechanism Verification

| Indicator | Status |
|-----------|--------|
| descriptors_computed | PASS |
| all_clusters_analyzed | {'PASS' if results['n_clusters'] == config.n_clusters else 'FAIL'} |
| variance_computed | PASS |
| effect_measurable | {'PASS' if any(r > 1.0 for r in results['variance_ratios'].values()) else 'FAIL'} |
| hypothesis_supported | {'PASS' if gate_pass else 'FAIL'} |

---

## Figures Generated

"""
    for path in results['figure_paths']:
        report += f"- `{path}`\n"

    report += f"""
---

## Conclusion

The MECHANISM hypothesis is **{'SUPPORTED' if gate_pass else 'NOT SUPPORTED'}**.

{'Shape descriptors successfully differentiate cluster centroids with variance ratio > 2.0 on ' + str(results["n_passing_descriptors"]) + ' descriptors.' if gate_pass else 'Shape descriptors did not show sufficient differentiation (variance ratio > 2.0 on >= 2 descriptors).'}

**Passing Descriptors**: {', '.join(results['passing_descriptors']) if results['passing_descriptors'] else 'None'}

**Key Findings**:
- {results['n_passing_descriptors']} of {len(results['descriptor_names'])} descriptors exceed variance ratio threshold
- Cluster profiles are {'distinct' if results['distinct_profiles'] else 'not distinct'} (min distance = {results['min_pairwise_distance']:.4f})
- Shape-based analysis {'reveals' if gate_pass else 'does not reveal'} meaningful differentiation between adoption trajectory clusters

**Next Step**: {'Proceed to h-m3 (archetype recovery)' if gate_pass else 'Document limitation and proceed to h-m3'}
"""

    # Write to file
    with open(config.output_path, 'w') as f:
        f.write(report)

    print(f"Validation report written to {config.output_path}")
    return gate_result
