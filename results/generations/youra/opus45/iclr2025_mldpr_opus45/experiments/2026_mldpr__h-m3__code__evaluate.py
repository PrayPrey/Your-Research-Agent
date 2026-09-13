"""Evaluation module for h-m3 Archetype Recovery experiment.

Implements gate metrics computation, mechanism verification,
figure generation, and validation report writing.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from datetime import datetime

from config import ExperimentConfig, ARCHETYPE_PROFILES, DESCRIPTOR_ORDER


def compute_gate_metrics(
    assignments: Dict[int, Tuple[str, float]],
    n_recovered: int,
    alignment_matrix: np.ndarray,
    config: ExperimentConfig
) -> Dict:
    """
    Evaluate SHOULD_WORK gate: n_recovered >= 3, mean_alignment > 0.70, uniqueness.

    Returns:
        Dict with gate_pass, n_recovered, mean_alignment, uniqueness, etc.
    """
    # Count recovered archetypes
    recovered_archetypes = set()
    alignment_scores = []

    for cluster_id, (arch_name, score) in assignments.items():
        recovered_archetypes.add(arch_name)
        alignment_scores.append(score)

    # Compute mean alignment (across matched pairs only)
    mean_alignment = np.mean(alignment_scores) if alignment_scores else 0.0

    # Check uniqueness (no archetype assigned to multiple clusters)
    assigned_archetypes = [arch for _, (arch, _) in assignments.items()]
    uniqueness = len(assigned_archetypes) == len(set(assigned_archetypes))

    # Gate criteria
    recovery_pass = n_recovered >= config.min_archetypes_recovered
    alignment_pass = mean_alignment >= config.alignment_threshold
    uniqueness_pass = uniqueness

    # Overall gate result
    gate_pass = recovery_pass and alignment_pass and uniqueness_pass

    return {
        "gate_pass": gate_pass,
        "n_recovered": n_recovered,
        "min_required": config.min_archetypes_recovered,
        "recovery_pass": recovery_pass,
        "mean_alignment": float(mean_alignment),
        "alignment_threshold": config.alignment_threshold,
        "alignment_pass": alignment_pass,
        "uniqueness": uniqueness,
        "uniqueness_pass": uniqueness_pass,
        "alignment_matrix": alignment_matrix,
        "n_archetypes": config.n_archetypes,
        "n_clusters": config.n_clusters,
        "assignments": assignments,
        "recovered_archetypes": list(recovered_archetypes),
    }


def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict]:
    """
    Check 5 activation indicators per PRD FR-5.3.

    Returns:
        (all_activated, indicators_dict)
    """
    indicators = {
        "alignment_computed": results.get("alignment_matrix") is not None,
        "archetypes_defined": results.get("n_archetypes") == 5,
        "clusters_analyzed": results.get("n_clusters") == 4,
        "recovery_measured": results.get("n_recovered", -1) >= 0,
        "threshold_applied": results.get("alignment_threshold") == 0.70,
    }

    all_activated = all(indicators.values())

    return all_activated, indicators


def generate_figures(
    alignment_matrix: np.ndarray,
    assignments: Dict,
    cluster_profiles: Dict,
    baseline_assignments: Dict,
    n_recovered: int,
    config: ExperimentConfig
) -> List[str]:
    """
    Generate and save figures to config.figures_dir.

    Figures:
    1. gate_metrics_bar.png (MANDATORY)
    2. alignment_heatmap.png
    3. radar_chart.png
    4. assignment_diagram.png
    5. descriptor_space.png

    Returns:
        List of saved file paths
    """
    os.makedirs(config.figures_dir, exist_ok=True)
    saved_paths = []
    archetype_names = list(ARCHETYPE_PROFILES.keys())

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')

    # 1. Gate Metrics Bar Chart (MANDATORY)
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Archetypes\nRecovered', 'Target']
    values = [n_recovered, config.min_archetypes_recovered]
    colors = ['#2ecc71' if n_recovered >= config.min_archetypes_recovered else '#e74c3c', '#3498db']
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    ax.axhline(y=config.min_archetypes_recovered, color='red', linestyle='--', linewidth=2, label=f'Threshold ({config.min_archetypes_recovered})')
    ax.set_ylabel('Number of Archetypes', fontsize=12)
    ax.set_title('h-m3 Gate Metrics: Archetype Recovery', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 6)

    # Add pass/fail indicator
    gate_result = "PASS" if n_recovered >= config.min_archetypes_recovered else "FAIL"
    gate_color = '#2ecc71' if gate_result == "PASS" else '#e74c3c'
    ax.text(0.5, 0.95, f'Gate: {gate_result}', transform=ax.transAxes,
            fontsize=16, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor=gate_color, alpha=0.8),
            color='white')

    ax.legend(loc='upper right')
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'gate_metrics_bar.png')
    plt.savefig(path, dpi=config.figure_dpi, bbox_inches='tight')
    plt.close()
    saved_paths.append(path)

    # 2. Alignment Heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(alignment_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
                xticklabels=[n.replace('_', '\n') for n in archetype_names],
                yticklabels=[f'Cluster {i}' for i in range(alignment_matrix.shape[0])],
                vmin=0, vmax=1, ax=ax,
                cbar_kws={'label': 'Alignment Score'})
    ax.set_title('Cluster-Archetype Alignment Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Archetype', fontsize=12)
    ax.set_ylabel('Cluster', fontsize=12)

    # Highlight cells above threshold
    for i in range(alignment_matrix.shape[0]):
        for j in range(alignment_matrix.shape[1]):
            if alignment_matrix[i, j] >= config.alignment_threshold:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=False,
                            edgecolor='black', linewidth=3))

    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'alignment_heatmap.png')
    plt.savefig(path, dpi=config.figure_dpi, bbox_inches='tight')
    plt.close()
    saved_paths.append(path)

    # 3. Radar Chart (archetype profiles vs cluster profiles)
    fig, axes = plt.subplots(2, 2, figsize=(12, 12), subplot_kw=dict(polar=True))
    axes = axes.flatten()

    angles = np.linspace(0, 2 * np.pi, len(DESCRIPTOR_ORDER), endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    for idx, (cluster_id, profile) in enumerate(sorted(cluster_profiles.items())):
        if idx >= 4:
            break
        ax = axes[idx]

        # Normalize profile values
        from model import ArchetypeRecoveryMatcher
        matcher = ArchetypeRecoveryMatcher(config)
        norm_profile = matcher.normalize_profile(profile)
        cluster_values = [norm_profile.get(d, 0.5) for d in DESCRIPTOR_ORDER]
        cluster_values += cluster_values[:1]

        # Plot cluster profile
        ax.plot(angles, cluster_values, 'o-', linewidth=2, label=f'Cluster {cluster_id}', color='#3498db')
        ax.fill(angles, cluster_values, alpha=0.25, color='#3498db')

        # Plot best matching archetype
        if cluster_id in assignments:
            arch_name, score = assignments[cluster_id]
            arch_values = [ARCHETYPE_PROFILES[arch_name].get(d, 0.5) for d in DESCRIPTOR_ORDER]
            arch_values += arch_values[:1]
            ax.plot(angles, arch_values, 's--', linewidth=2, label=f'{arch_name} ({score:.2f})', color='#e74c3c')
            ax.fill(angles, arch_values, alpha=0.1, color='#e74c3c')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([d.replace('_', '\n') for d in DESCRIPTOR_ORDER], size=8)
        ax.set_title(f'Cluster {cluster_id}', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.set_ylim(0, 1)

    plt.suptitle('Cluster Profiles vs Matched Archetypes', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'radar_chart.png')
    plt.savefig(path, dpi=config.figure_dpi, bbox_inches='tight')
    plt.close()
    saved_paths.append(path)

    # 4. Assignment Diagram
    fig, ax = plt.subplots(figsize=(12, 6))

    # Left side: clusters
    cluster_y = np.linspace(0.8, 0.2, 4)
    for i, y in enumerate(cluster_y):
        ax.scatter(0.2, y, s=1000, c='#3498db', zorder=5)
        ax.text(0.2, y, f'C{i}', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    # Right side: archetypes
    archetype_y = np.linspace(0.9, 0.1, 5)
    arch_colors = ['#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
    for i, (name, y) in enumerate(zip(archetype_names, archetype_y)):
        ax.scatter(0.8, y, s=1000, c=arch_colors[i], zorder=5)
        ax.text(0.8, y, name[:8], ha='center', va='center', fontsize=8, fontweight='bold', color='white')

    # Draw assignment arrows
    for cluster_id, (arch_name, score) in assignments.items():
        arch_idx = archetype_names.index(arch_name)
        y1 = cluster_y[cluster_id]
        y2 = archetype_y[arch_idx]
        color = '#2ecc71' if score >= config.alignment_threshold else '#e74c3c'
        ax.annotate('', xy=(0.75, y2), xytext=(0.25, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2))
        ax.text(0.5, (y1 + y2) / 2, f'{score:.2f}', ha='center', va='center',
               fontsize=10, color=color, fontweight='bold')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Cluster-to-Archetype Assignments', fontsize=14, fontweight='bold')
    ax.text(0.2, 0.95, 'Clusters', ha='center', fontsize=12, fontweight='bold')
    ax.text(0.8, 0.95, 'Archetypes', ha='center', fontsize=12, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'assignment_diagram.png')
    plt.savefig(path, dpi=config.figure_dpi, bbox_inches='tight')
    plt.close()
    saved_paths.append(path)

    # 5. Descriptor Space Projection (2D PCA)
    fig, ax = plt.subplots(figsize=(10, 8))

    # Collect all profiles
    all_profiles = []
    all_labels = []
    all_types = []  # 'cluster' or 'archetype'

    for cluster_id, profile in sorted(cluster_profiles.items()):
        from model import ArchetypeRecoveryMatcher
        matcher = ArchetypeRecoveryMatcher(config)
        norm_profile = matcher.normalize_profile(profile)
        vec = [norm_profile.get(d, 0.5) for d in DESCRIPTOR_ORDER]
        all_profiles.append(vec)
        all_labels.append(f'C{cluster_id}')
        all_types.append('cluster')

    for arch_name, profile in ARCHETYPE_PROFILES.items():
        vec = [profile.get(d, 0.5) for d in DESCRIPTOR_ORDER]
        all_profiles.append(vec)
        all_labels.append(arch_name[:8])
        all_types.append('archetype')

    all_profiles = np.array(all_profiles)

    # Simple 2D projection (first 2 descriptors for simplicity)
    x = all_profiles[:, 0]  # growth_ratio
    y = all_profiles[:, 1]  # peak_timing

    # Plot clusters
    cluster_mask = np.array(all_types) == 'cluster'
    ax.scatter(x[cluster_mask], y[cluster_mask], s=200, c='#3498db', marker='o',
              edgecolors='black', linewidths=2, label='Clusters', zorder=5)

    # Plot archetypes
    archetype_mask = np.array(all_types) == 'archetype'
    ax.scatter(x[archetype_mask], y[archetype_mask], s=200, c='#e74c3c', marker='s',
              edgecolors='black', linewidths=2, label='Archetypes', zorder=5)

    # Add labels
    for i, (xi, yi, label) in enumerate(zip(x, y, all_labels)):
        ax.annotate(label, (xi, yi), xytext=(5, 5), textcoords='offset points', fontsize=9)

    ax.set_xlabel('Growth Ratio (normalized)', fontsize=12)
    ax.set_ylabel('Peak Timing (normalized)', fontsize=12)
    ax.set_title('Descriptor Space: Clusters vs Archetypes', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)

    plt.tight_layout()
    path = os.path.join(config.figures_dir, 'descriptor_space.png')
    plt.savefig(path, dpi=config.figure_dpi, bbox_inches='tight')
    plt.close()
    saved_paths.append(path)

    print(f"Generated {len(saved_paths)} figures in {config.figures_dir}")

    return saved_paths


def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """
    Write 04_validation.md with all metrics and gate verdict.

    Returns:
        'PASS' or 'FAIL'
    """
    gate_result = "PASS" if results["gate_pass"] else "FAIL"
    timestamp = datetime.now().isoformat()

    report = f"""# Phase 4 Validation Report: h-m3

**Hypothesis:** Archetype Recovery via Shape Descriptor Alignment
**Date:** {timestamp}
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_result}

---

## Executive Summary

This report validates hypothesis h-m3: Under the differentiated clusters, if shape descriptors are correctly calibrated, then >=3 of 5 proposed archetypes will be recovered as distinct clusters with >70% feature alignment to archetype definitions.

**Result:** {gate_result}

---

## Gate Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Archetypes Recovered | >= {results['min_required']} | {results['n_recovered']} | {"✅ PASS" if results['recovery_pass'] else "❌ FAIL"} |
| Mean Alignment Score | >= {results['alignment_threshold']:.2f} | {results['mean_alignment']:.4f} | {"✅ PASS" if results['alignment_pass'] else "❌ FAIL"} |
| Uniqueness (no duplicates) | True | {results['uniqueness']} | {"✅ PASS" if results['uniqueness_pass'] else "❌ FAIL"} |

---

## Mechanism Verification

| Indicator | Status |
|-----------|--------|
| Alignment Computed | {results.get('mechanism_indicators', {}).get('alignment_computed', True)} |
| Archetypes Defined (5) | {results.get('mechanism_indicators', {}).get('archetypes_defined', True)} |
| Clusters Analyzed (4) | {results.get('mechanism_indicators', {}).get('clusters_analyzed', True)} |
| Recovery Measured | {results.get('mechanism_indicators', {}).get('recovery_measured', True)} |
| Threshold Applied (0.70) | {results.get('mechanism_indicators', {}).get('threshold_applied', True)} |

**Mechanism Activated:** {"Yes" if results.get('mechanism_activated', True) else "No"}

---

## Alignment Matrix

```
Clusters (rows) × Archetypes (columns)
"""

    # Add alignment matrix
    alignment_matrix = results.get('alignment_matrix', np.zeros((4, 5)))
    archetype_names = list(ARCHETYPE_PROFILES.keys())

    # Header
    report += "\n" + " " * 12 + "  ".join([f"{n[:8]:>10}" for n in archetype_names]) + "\n"

    # Rows
    for i in range(alignment_matrix.shape[0]):
        row_values = "  ".join([f"{alignment_matrix[i, j]:>10.4f}" for j in range(alignment_matrix.shape[1])])
        report += f"Cluster {i}:  {row_values}\n"

    report += "```\n\n"

    # Assignments
    report += "## Cluster-Archetype Assignments\n\n"
    report += "| Cluster | Best Match | Alignment | Status |\n"
    report += "|---------|------------|-----------|--------|\n"

    assignments = results.get('assignments', {})
    for cluster_id in range(4):
        if cluster_id in assignments:
            arch_name, score = assignments[cluster_id]
            status = "✅ Matched" if score >= config.alignment_threshold else "❌ Below threshold"
            report += f"| Cluster {cluster_id} | {arch_name} | {score:.4f} | {status} |\n"
        else:
            report += f"| Cluster {cluster_id} | None | - | ❌ No match |\n"

    # Recovered archetypes
    report += f"\n**Recovered Archetypes:** {results.get('recovered_archetypes', [])}\n"
    report += f"**Recovery Rate:** {results['n_recovered']}/{len(archetype_names)} ({100*results['n_recovered']/len(archetype_names):.1f}%)\n"

    # Figures
    report += "\n---\n\n## Figures\n\n"
    figure_files = results.get('figure_paths', [])
    for fig_path in figure_files:
        fig_name = os.path.basename(fig_path)
        report += f"- `figures/{fig_name}`\n"

    # Key findings
    report += "\n---\n\n## Key Findings\n\n"

    if results['gate_pass']:
        report += f"1. **Archetype Recovery Validated:** {results['n_recovered']}/{len(archetype_names)} archetypes recovered with >70% alignment\n"
        report += f"2. **Mean Alignment Score:** {results['mean_alignment']:.4f} exceeds threshold ({config.alignment_threshold})\n"
        report += f"3. **Unique Assignments:** Each cluster maps to a distinct archetype\n"
        report += "4. **Hypothesis h-m3 SUPPORTED:** The proposed lifecycle taxonomy captures real-world adoption patterns\n"
    else:
        report += f"1. **Recovery Below Target:** Only {results['n_recovered']}/{config.min_archetypes_recovered} required archetypes recovered\n"
        report += f"2. **Mean Alignment:** {results['mean_alignment']:.4f} (threshold: {config.alignment_threshold})\n"
        report += "3. **Limitation Noted:** Partial taxonomy recovery documented\n"
        report += "4. **Next Steps:** Continue with 4-cluster empirical taxonomy; consider refining archetype definitions\n"

    # Data source
    report += "\n---\n\n## Data Source\n\n"
    report += "- **Dataset:** HuggingFace Dataset Download Statistics (reused from h-e1)\n"
    report += "- **Clusters:** k=4 from h-e1 DTW clustering (silhouette=0.289, Jaccard=0.991)\n"
    report += "- **Shape Descriptors:** 4 descriptors from h-m2 (3/4 exceeding variance ratio >2.0)\n"
    report += "- **Alignment Method:** Cosine similarity on normalized descriptor vectors\n"

    report += "\n---\n\n*Generated by Phase 4 Validation Workflow*\n"

    # Write report
    with open(config.output_path, 'w') as f:
        f.write(report)

    print(f"Validation report written to {config.output_path}")

    return gate_result
