"""
Configuration for H-E1: Curvature Subspace Alignment Experiment
LIGHT tier infrastructure - hardcoded dictionary configuration
"""

CONFIG = {
    # Reproducibility
    "seed": 42,

    # Dataset
    "data_dir": "./data/waterbird_complete95_forest2water2/",
    "batch_size": 128,
    "num_workers": 4,
    "num_classes": 2,
    "num_groups": 4,

    # Model
    "model_name": "resnet50",
    "pretrained": True,

    # Training - ERM
    "epochs": 100,
    "lr": 0.001,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "lr_milestones": [60, 80],
    "lr_gamma": 0.1,
    "patience": 10,

    # Training - Group-DRO
    "dro_step_size": 0.01,

    # Hessian Analysis
    "num_eigenthings": 100,
    "power_iter_steps": 20,
    "hessian_batch_size": 32,

    # Marchenko-Pastur Fitting
    "mp_fit_range": (20, 80),

    # Paths
    "checkpoint_dir": "./checkpoints/",
    "results_dir": "./results/",
    "figures_dir": "./figures/",

    # Logging
    "log_interval": 10,
}

VIZ_CONFIG = {
    # Figure settings
    "figsize_bar": (8, 6),
    "figsize_spectrum": (10, 6),
    "figsize_curves": (10, 6),
    "figsize_heatmap": (8, 6),
    "figsize_scatter": (8, 6),
    "dpi": 300,
    "format": "png",

    # Colors
    "color_erm": "red",
    "color_dro": "blue",
    "color_bulk_edge": "red",
    "alpha": 0.7,

    # Output paths
    "fig_alignment": "fig1_alignment_comparison.png",
    "fig_spectrum_erm": "fig2_hessian_spectrum_erm.png",
    "fig_spectrum_dro": "fig3_hessian_spectrum_dro.png",
    "fig_training": "fig4_training_curves.png",
    "fig_heatmap": "fig5_group_accuracy_heatmap.png",
}

SMOKE_TEST_CONFIG = {
    # Reduced dataset
    "smoke_num_samples": 100,
    "smoke_batch_size": 16,

    # Reduced training
    "smoke_epochs": 1,
    "smoke_num_eigenthings": 10,

    # Quick validation
    "smoke_timeout": 300,
}
