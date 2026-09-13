# Configuration for H-E1: Operation-Specific Weight Signal Existence
# Generated from 03_config.md

CONFIG = {
    # Global settings
    "hypothesis_id": "H-E1",
    "random_seed": 42,

    # Model Zoo Collection (A-1)
    "model_zoo": {
        "n_resnet": 50,
        "n_vit": 50,
        "architectures": ["resnet50", "vit_base_patch16_224"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3,
        "min_success_rate": 0.90
    },

    # Feature Extraction (A-2)
    "features": {
        "include_spectral": True,
        "top_k_spectral": 5,
        "skip_biases": True,
        "skip_frozen": True,
        "batch_size": 10
    },

    # Classification (A-3)
    "train_test_split": {
        "test_size": 0.3,
        "stratify": True,
        "random_state": 42
    },
    "classifier": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "random_state": 42
    },

    # Statistical Testing (A-4)
    "statistical_test": {
        "n_permutations": 1000,
        "alpha": 0.05
    },

    # Visualization
    "visualization": {
        "dpi": 300,
        "style": "seaborn"
    },

    # Success Criteria
    "success_criteria": {
        "target_accuracy": 0.80,
        "partial_threshold": 0.70,
        "min_p_value": 0.05,
        "min_ablation_improvement": 0.05
    },

    # Directory Structure
    "directories": {
        "data": "data/",
        "models": "models/",
        "results": "results/",
        "figures": "figures/"
    }
}
