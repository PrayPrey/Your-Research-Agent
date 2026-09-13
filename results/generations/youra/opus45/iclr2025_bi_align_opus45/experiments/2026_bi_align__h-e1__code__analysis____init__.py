"""Analysis module for statistical analysis and visualization."""

from .stats import (
    cohens_d,
    cohens_d_ci,
    paired_ttest,
    pooled_effect_size,
    heterogeneity_test,
    compute_per_rm_stats,
    compute_aggregate_stats,
    check_gate_condition,
    export_results,
)

from .visualize import (
    plot_forest,
    plot_violin,
    plot_interaction,
    plot_gate_metrics,
    generate_all_figures,
)

__all__ = [
    "cohens_d",
    "cohens_d_ci",
    "paired_ttest",
    "pooled_effect_size",
    "heterogeneity_test",
    "compute_per_rm_stats",
    "compute_aggregate_stats",
    "check_gate_condition",
    "export_results",
    "plot_forest",
    "plot_violin",
    "plot_interaction",
    "plot_gate_metrics",
    "generate_all_figures",
]
