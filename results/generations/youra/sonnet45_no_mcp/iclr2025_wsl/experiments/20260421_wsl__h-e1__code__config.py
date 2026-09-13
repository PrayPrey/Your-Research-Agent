# Configuration for h-e1: Weight-Based Depth Classification
# Generated from Phase 3 specifications

CONFIG = {
    # Dataset: 20 pretrained ImageNet CNNs
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

    # Data splitting
    "test_size": 0.2,  # 80/20 split: 16 train, 4 test
    "stratify": True,  # Maintain class balance
    "random_state": 42,  # Reproducibility

    # Feature normalization
    "scaler": {
        "with_mean": True,  # Center to mean=0
        "with_std": True,   # Scale to std=1
    },

    # Binary classifier (sklearn defaults)
    "classifier": {
        "C": 1.0,  # sklearn default regularization
        "solver": "lbfgs",  # sklearn default solver
        "max_iter": 1000,  # Sufficient for n=16 samples
        "random_state": 42,
    },

    # Gate evaluation
    "gate_threshold": 0.70,  # MUST_WORK threshold
    "baseline_accuracy": 0.50,  # Random guessing baseline

    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "../figures",
    "figure_dpi": 300,  # Publication quality
}
