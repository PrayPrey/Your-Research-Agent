# Configuration for h-e1 Experiment
# Date: 2026-04-20
# Hypothesis: EXISTENCE - Confidence-Timeout Correlation

EXPERIMENT_CONFIG = {
    # Dataset
    "repo_url": "https://github.com/leanprover-community/mathlib",
    "commit_hash": "d88406ff7d5d41304c2f94222ac7852ecb4c38f2",  # LeanDojo Benchmark default
    "sample_size": 100,
    "random_seed": 42,

    # Experiment execution
    "timeout_seconds": 300,
    "confidence_window": 15,

    # Gate condition
    "target_correlation": 0.3,
    "significance_level": 0.05,

    # Output paths
    "results_dir": "./results",
    "figures_dir": "./figures",

    # Logging
    "log_level": "INFO",
    "progress_interval": 10,  # Print progress every N theorems
}

VISUALIZATION_CONFIG = {
    # Output settings
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",

    # Figure size (inches)
    "figsize": (10, 6),

    # Color scheme
    "colors": {
        "success": "#2ecc71",  # Green
        "timeout": "#e74c3c",  # Red
        "target": "#3498db",   # Blue
    },

    # Gate metrics plot
    "gate_plot": {
        "target_correlation": 0.3,
        "bar_width": 0.35,
        "show_pvalue": True,
    },

    # Scatter plot
    "scatter": {
        "alpha": 0.6,
        "marker_size": 50,
        "jitter": 0.02,  # Vertical jitter for binary outcomes
    },

    # Distribution plots
    "distribution": {
        "bins": 20,
        "alpha": 0.7,
        "kde": True,  # Kernel density estimation overlay
    },

    # Trajectory examples
    "trajectory": {
        "n_examples_per_class": 3,
        "linewidth": 2,
        "show_std_band": False,  # Disabled for EXISTENCE simplicity
    },

    # ROC curve
    "roc": {
        "linewidth": 2,
        "show_diagonal": True,
        "show_auc": True,
    },
}
