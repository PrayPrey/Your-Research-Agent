# Configuration for h-m2: Architectural Constraints Mechanism Validation
# Generated from Phase 3 specifications
# Extends h-m1 with architectural constraint features

CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m2",
    "experiment_name": "Architectural Constraints Mechanism Validation",
    "base_hypothesis": "h-m1",

    # Dataset: Same 20 pretrained ImageNet CNNs as h-e1 and h-m1
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

    # Data splitting (identical to h-m1)
    "test_size": 0.2,  # 80/20 split: 16 train, 4 test
    "stratify": True,  # Maintain class balance
    "random_state": 42,  # Reproducibility

    # Feature extraction (NEW for h-m2)
    "feature_extractor": {
        "type": "ArchitecturalFeatureExtractor",
        "n_features": 8,  # Architectural constraint features
    },

    # Feature normalization (identical to h-m1)
    "scaler": {
        "with_mean": True,  # Center to mean=0
        "with_std": True,   # Scale to std=1
    },

    # Binary classifier (h-m1 optimal hyperparameters)
    "classifier": {
        "C": 1.0,  # h-m1 optimal regularization
        "solver": "lbfgs",  # h-m1 optimal solver
        "max_iter": 1000,  # Sufficient for n=16 samples
        "random_state": 42,
    },

    # Within-family validation (NEW for h-m2)
    "within_family_threshold": 0.65,
    "architecture_families": {
        "resnet": ["resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
                   "wide_resnet50_2", "wide_resnet101_2", "resnext50_32x4d", "resnext101_32x8d"],
        "vgg": ["vgg11", "vgg13", "vgg16", "vgg19"],
        "densenet": ["densenet121", "densenet161", "densenet169", "densenet201"],
    },

    # Validation
    "run_random_test": True,  # Enable random initialization test

    # Gate evaluation
    "gate_threshold": 0.50,  # SHOULD_WORK threshold
    "baseline_accuracy": 0.50,  # Random guessing baseline
    "h_e1_accuracy": 1.0,  # h-e1 baseline
    "h_m1_accuracy": 1.0,  # h-m1 baseline

    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
    "figure_dpi": 150,  # High quality
}
