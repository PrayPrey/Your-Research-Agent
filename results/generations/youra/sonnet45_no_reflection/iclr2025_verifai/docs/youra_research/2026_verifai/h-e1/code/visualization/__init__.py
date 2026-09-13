"""Visualization module for heterogeneity analysis."""
from .plots import (
    plot_gate_comparison,
    plot_dn_distribution,
    plot_entropy_distribution,
    plot_dn_vs_entropy_scatter,
    plot_quartile_boxplot,
    generate_all_figures
)

__all__ = [
    'plot_gate_comparison',
    'plot_dn_distribution',
    'plot_entropy_distribution',
    'plot_dn_vs_entropy_scatter',
    'plot_quartile_boxplot',
    'generate_all_figures'
]
