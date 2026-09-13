"""Configuration for MNIST horizontal flip augmentation study."""
import torch

# Model architecture (PyTorch official MNIST example)
MODEL_CONFIG = {
    "conv1_out_channels": 32,
    "conv2_out_channels": 64,
    "fc1_out_features": 128,
    "num_classes": 10,
    "dropout1": 0.25,
    "dropout2": 0.5,
}

# Training hyperparameters (PyTorch official defaults)
TRAINING_CONFIG = {
    "optimizer": "adadelta",
    "lr": 1.0,
    "scheduler": "step_lr",
    "step_size": 1,
    "gamma": 0.7,
    "epochs": 14,
    "batch_size": 64,
    "seed": 42,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}

# Data configuration
DATA_CONFIG = {
    "dataset": "MNIST",
    "data_root": "./data",
    "mean": 0.1307,
    "std": 0.3081,
    "download": True,
    "num_workers": 4,
}

# Experiment conditions
EXPERIMENT_CONFIG = {
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],
    "symmetric_digits": [0, 1, 8],
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],
    "rotation_degrees": 15,
}

# Output paths
OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-e1",
    "figures_dir": "docs/youra_research/h-e1/figures",
    "results_file": "results_accuracy.json",
    "logs_file": "training_logs.txt",
    "gate_file": "gate_decision.json",
}
