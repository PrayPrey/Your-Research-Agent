"""Configuration for MNIST dose-response mechanism testing (h-m)."""
import torch

# ========================================
# INHERITED FROM h-e1 (NO CHANGES)
# ========================================

MODEL_CONFIG = {
    "conv1_out_channels": 32,
    "conv2_out_channels": 64,
    "fc1_out_features": 128,
    "num_classes": 10,
    "dropout1": 0.25,
    "dropout2": 0.5,
}

DATA_CONFIG = {
    "dataset": "MNIST",
    "data_root": "./data",
    "mean": 0.1307,
    "std": 0.3081,
    "download": True,
    "num_workers": 4,
}

EXPERIMENT_CONFIG = {
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],
    "symmetric_digits": [0, 1, 8],
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],
    "rotation_degrees": 15,
}

# ========================================
# EXTENDED FOR h-m: Multi-Seed Training
# ========================================

TRAINING_CONFIG = {
    "optimizer": "adadelta",
    "lr": 1.0,
    "scheduler": "step_lr",
    "step_size": 1,
    "gamma": 0.7,
    "epochs": 14,
    "batch_size": 64,
    "seeds": [42, 123, 456, 789, 1011],  # EXTENDED: 5 seeds for statistical testing
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}

# ========================================
# NEW FOR h-m: Statistical Testing
# ========================================

STATS_CONFIG = {
    "correlation_method": "spearman",  # Spearman rank correlation
    "alpha": 0.05,  # Significance level
    "flip_probabilities": [0.0, 0.3, 0.5, 0.9],  # For dose-response mapping
}

# ========================================
# EXTENDED FOR h-m: Multi-Seed Outputs
# ========================================

OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-m",
    "figures_dir": "docs/youra_research/h-m/figures",
    "results_file": "per_seed_results.csv",  # EXTENDED: CSV instead of JSON
    "stats_file": "dose_response_stats.json",  # NEW: Statistical test results
    "logs_dir": "training_logs",  # NEW: Per-seed training logs
    "checkpoints_dir": "model_checkpoints",  # NEW: Per (condition, seed) models
    "gate_file": "gate_decision.json",
}
