"""
Visualization module for H-E1.
Generates figures for the LLM Documentation-Benchmark Registry.
"""
import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config


def plot_doc_score_distribution(registry_df: pd.DataFrame, output_path: str) -> None:
    """Histogram of doc_score (0-4). Saves to output_path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    if 'doc_score' in registry_df.columns:
        counts = registry_df['doc_score'].value_counts().sort_index()
        ax.bar(counts.index, counts.values, color='steelblue', edgecolor='white')
        ax.set_xlabel('Documentation Score (0-4)', fontsize=12)
        ax.set_ylabel('Number of Models', fontsize=12)
        ax.set_title('Distribution of Documentation Scores\nAcross Open LLM Leaderboard Models', fontsize=13)
        ax.set_xticks([0, 1, 2, 3, 4])
        n = len(registry_df)
        mean_score = registry_df['doc_score'].mean()
        ax.text(0.98, 0.95, f'N={n}\nMean={mean_score:.2f}',
                transform=ax.transAxes, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_dropout_funnel(funnel_counts: dict, output_path: str) -> None:
    """Waterfall/bar chart of funnel stages. funnel_counts: ordered stage->count dict."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))

    stages = list(funnel_counts.keys())
    counts = list(funnel_counts.values())

    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(stages)))
    bars = ax.bar(range(len(stages)), counts, color=colors, edgecolor='white')

    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels(stages, rotation=30, ha='right', fontsize=10)
    ax.set_ylabel('Number of Models', fontsize=12)
    ax.set_title('Data Collection Dropout Funnel', fontsize=13)

    # Add count labels on bars
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 10,
                str(count), ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_feature_coverage(registry_df: pd.DataFrame, output_path: str) -> None:
    """4-panel bar chart of fraction of models with each binary feature=1."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    feature_labels = {
        'dedup_documented': 'Deduplication',
        'perplexity_filter_documented': 'Perplexity Filter',
        'domain_composition_documented': 'Domain Composition',
        'decontamination_documented': 'Decontamination',
    }

    available_feats = [f for f in config.FEATURE_COLS if f in registry_df.columns]
    fractions = [registry_df[f].mean() for f in available_feats]
    labels = [feature_labels.get(f, f) for f in available_feats]

    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
    ax.bar(range(len(labels)), fractions, color=colors[:len(labels)], edgecolor='white')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=10)
    ax.set_ylabel('Fraction of Models', fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_title('Curation Feature Coverage Across Registry', fontsize=13)

    # Add percentage labels
    for i, frac in enumerate(fractions):
        ax.text(i, frac + 0.02, f'{frac:.1%}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_family_breakdown(registry_df: pd.DataFrame, output_path: str) -> None:
    """Stacked bar: arch_family x doc_score distribution."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))

    if 'arch_family' in registry_df.columns and 'doc_score' in registry_df.columns:
        families = registry_df['arch_family'].value_counts().head(6).index.tolist()
        doc_scores = sorted(registry_df['doc_score'].unique())

        x = np.arange(len(families))
        bottom = np.zeros(len(families))
        colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(doc_scores)))

        for score, color in zip(doc_scores, colors):
            counts = []
            for fam in families:
                subset = registry_df[registry_df['arch_family'] == fam]
                counts.append((subset['doc_score'] == score).sum())
            ax.bar(x, counts, bottom=bottom, label=f'Score={score}', color=color)
            bottom += np.array(counts)

        ax.set_xticks(x)
        ax.set_xticklabels(families, fontsize=10)
        ax.set_ylabel('Number of Models', fontsize=12)
        ax.set_title('Documentation Score Distribution by Architecture Family', fontsize=12)
        ax.legend(title='Doc Score', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_benchmark_heatmap(registry_df: pd.DataFrame, output_path: str) -> None:
    """Heatmap: model x benchmark availability (binary non-null matrix)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    benchmark_cols = [c for c in config.BENCHMARK_COLS if c in registry_df.columns]

    if benchmark_cols:
        # Sample up to 100 models for readability
        sample_df = registry_df.head(100) if len(registry_df) > 100 else registry_df

        # Binary availability matrix
        avail_matrix = sample_df[benchmark_cols].notna().astype(int)

        im = ax.imshow(avail_matrix.T, aspect='auto', cmap='Blues', vmin=0, vmax=1)
        ax.set_yticks(range(len(benchmark_cols)))
        ax.set_yticklabels(benchmark_cols, fontsize=10)
        ax.set_xlabel('Model Index', fontsize=12)
        ax.set_title('Benchmark Score Availability\n(Blue = Available)', fontsize=12)

        # Show overall availability
        for j, bench in enumerate(benchmark_cols):
            overall = avail_matrix[bench].mean()
            ax.text(len(avail_matrix) + 1, j, f'{overall:.0%}',
                    ha='left', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
