"""Configuration for H-M2 MECHANISM analysis."""

CONFIG = {
    # Input (h-e1 artifact)
    "H_E1_SCORES_CSV": "../h-e1/code/outputs/scores.csv",

    # Statistics
    "COHENS_D_THRESHOLD": 0.2,
    "ALPHA": 0.05,

    # Output
    "OUTPUT_DIR": "outputs",
    "METRICS_JSON": "outputs/metrics.json",
    "FIGURES_DIR": "figures",
    "DIST_PLOT_PNG": "figures/distribution_comparison.png",
    "HIST_PLOT_PNG": "figures/histogram_overlay.png",
}
