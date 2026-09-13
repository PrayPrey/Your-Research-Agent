"""Configuration for MNIST rotation augmentation study (h-c1 positive control)."""
import torch

# Model architecture (PyTorch official MNIST example - identical to h-e1 baseline)
MODEL_CONFIG = {
    "conv1_out_channels": 32,
    "conv2_out_channels": 64,
    "fc1_out_features": 128,
    "num_classes": 10,
    "dropout1": 0.25,
    "dropout2": 0.5,
}

# Training hyperparameters (Adam optimizer for rotation experiment)
TRAINING_CONFIG = {
    "optimizer": "adam",              # Adam standard for rotation augmentation
    "lr": 0.001,                      # Standard Adam LR (emrebaranarca repo)
    "weight_decay": 0.0,              # No weight decay (PyTorch official)
    "epochs": 30,                     # emrebaranarca repo standard
    "batch_size": 64,                 # PyTorch official default
    "seed": 42,                       # Reproducibility
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "early_stopping_patience": 5,     # Validation convergence check
}

# Data configuration
DATA_CONFIG = {
    "dataset": "MNIST",
    "data_root": "./data",
    "mean": 0.1307,                   # MNIST standard normalization
    "std": 0.3081,
    "download": True,
}

# Training configuration continued
TRAINING_CONFIG["num_workers"] = 4

# Experiment conditions
EXPERIMENT_CONFIG = {
    "conditions": ["baseline", "rotation"],  # Two conditions: no aug vs rotation
    "symmetric_digits": [0, 1, 8],
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],
    "rotation_degrees": 15,                  # ±15° (emrebaranarca repo, Phase 2B)
    "differential_threshold": 0.02,          # 2% threshold for success check
}

# Output paths
OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-c1",
    "figures_dir": "docs/youra_research/h-c1/figures",
    "checkpoints_dir": "docs/youra_research/h-c1/checkpoints",
    "logs_dir": "docs/youra_research/h-c1/logs",
    "results_file": "results_accuracy.json",
    "training_logs_file": "training_logs.json",
    "gate_file": "gate_decision.json",
}
