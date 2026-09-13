"""Configuration for h-m1 threshold classifier experiment."""

CONFIG = {
    # Data Configuration
    "data": {
        "h_e1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1/code/results/entropy_results.json",
        "entity_label": 0,
        "non_entity_label": 1
    },

    # Train/Test Split
    "split": {
        "train_ratio": 0.8,
        "test_size": 0.2,
        "stratify": True,
        "random_state": 42
    },

    # Threshold Classifier
    "classifier": {
        "threshold_min": 0.0,
        "threshold_max": 1.0,
        "threshold_steps": 101
    },

    # Evaluation Metrics
    "evaluation": {
        "metrics": ["accuracy", "precision", "recall", "f1"]
    },

    # Gate Check
    "gate": {
        "threshold": 0.70
    },

    # Baseline Comparison
    "baseline": {
        "random_state": 42
    },

    # Visualization
    "visualization": {
        "figures_dir": "./figures/",
        "figure_dpi": 300,
        "figure_format": "png"
    },

    # Output
    "output": {
        "results_file": "./results/classification_results.json",
        "figures_dir": "./figures/"
    },

    # Reproducibility
    "seed": 42
}
