"""Visualization of error mode distributions."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_error_distribution(
    distributions: dict[str, dict[str, float]],
    output_path: str,
    dpi: int = 300
) -> None:
    """
    Generate stacked bar chart of error distributions.

    Args:
        distributions: {benchmark: {error_mode: percentage}}
        output_path: Path to save PNG
        dpi: Image resolution
    """
    benchmarks = list(distributions.keys())
    n_benchmarks = len(benchmarks)

    # Extract percentages for each error mode
    syntax_pcts = [distributions[b].get("syntax", 0.0) for b in benchmarks]
    type_pcts = [distributions[b].get("type", 0.0) for b in benchmarks]
    semantic_pcts = [distributions[b].get("semantic", 0.0) for b in benchmarks]

    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(n_benchmarks)
    width = 0.6

    p1 = ax.bar(x, syntax_pcts, width, label='Syntax', color='#e74c3c')
    p2 = ax.bar(x, type_pcts, width, bottom=syntax_pcts, label='Type', color='#3498db')

    bottom = np.array(syntax_pcts) + np.array(type_pcts)
    p3 = ax.bar(x, semantic_pcts, width, bottom=bottom, label='Semantic', color='#2ecc71')

    ax.set_ylabel('Error Percentage (%)', fontsize=12)
    ax.set_title('Error Mode Distribution Across Benchmarks', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", " ").title() for b in benchmarks])
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add percentage labels on bars
    for i, bench in enumerate(benchmarks):
        total = 0
        for pcts, label in [(syntax_pcts, 'syntax'), (type_pcts, 'type'), (semantic_pcts, 'semantic')]:
            pct = pcts[i]
            if pct > 5:  # Only label if >5%
                ax.text(i, total + pct/2, f'{pct:.1f}%', ha='center', va='center', fontsize=9)
            total += pct

    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()

    print(f"Saved visualization to {output_path}")
