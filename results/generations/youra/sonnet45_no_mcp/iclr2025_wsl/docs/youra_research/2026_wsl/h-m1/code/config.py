# Configuration for h-m1: Gradient Flow Feature Validation
# Generated from Phase 3 specifications
# Reuses h-e1 optimal hyperparameters with gradient-flow features

CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m1",
    "experiment_name": "Gradient Flow Feature Validation",
    "base_hypothesis": "h-e1",

    # Dataset: Same 20 pretrained ImageNet CNNs as h-e1
    "shallow_models": [
        "resnet18", "resnet34",
        "vgg11", "vgg13", "vgg16", "vgg19",
        "alexnet", "squeezenet1_0",
        "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152",
        "densenet161", "densenet169", "densenet201",
        "wide_resnet50_2", "wide_resnet101_2",
        "resnext50_32x4d", "resnext101_32x8d"
    ],

    # Data splitting (identical to h-e1)
    "test_size": 0.2,  # 80/20 split: 16 train, 4 test
    "stratify": True,  # Maintain class balance
    "random_state": 42,  # Reproducibility

    # Feature extraction (NEW for h-m1)
    "feature_extractor": {
        "type": "GradientFlowFeatureExtractor",
        "n_features": 6,  # Changed from 4 (h-e1) to 6 (gradient-flow)
    },

    # Feature normalization (identical to h-e1)
    "scaler": {
        "with_mean": True,  # Center to mean=0
        "with_std": True,   # Scale to std=1
    },

    # Binary classifier (h-e1 optimal hyperparameters)
    "classifier": {
        "C": 1.0,  # h-e1 optimal regularization
        "solver": "lbfgs",  # h-e1 optimal solver
        "max_iter": 1000,  # Sufficient for n=16 samples
        "random_state": 42,
    },

    # Validation (NEW for h-m1)
    "run_random_test": True,  # Enable random initialization test

    # Gate evaluation
    "gate_threshold": 0.50,  # MUST_WORK threshold (gradient contribution)
    "baseline_accuracy": 0.50,  # Random guessing baseline
    "h_e1_accuracy": 1.0,  # h-e1 baseline for comparison

    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
    "figure_dpi": 150,  # High quality
}
