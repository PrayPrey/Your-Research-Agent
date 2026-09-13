# config.py - H-E1 Confidence Calibration Configuration
# Applied: Standard PyTorch defaults + Guo et al. 2017 calibration settings

CONFIG = {
    # Experiment metadata
    "experiment": {
        "name": "h-e1-confidence-calibration",
        "hypothesis_type": "EXISTENCE",
        "random_seed": 42,
        "n_folds": 10,
        "device": "cuda",  # or "cpu" if GPU unavailable
    },

    # Dataset acquisition and preparation
    "data": {
        "source": "codeforces",
        "dataset_name": "codecomplex",  # Primary: CodeComplex GitHub repo
        "min_samples": 500,
        "code_length_range": [10, 500],  # LOC filtering
        "runtime_variance_threshold": 0.20,  # CV < 20% required
        "n_runs_per_sample": 3,  # For runtime averaging
        "output_dir": "./data/codeforces",
        "cache_ast_features": True,

        # CV split ratios (per fold)
        "train_ratio": 0.80,  # 360 samples
        "val_ratio": 0.10,    # 45 samples (for temperature tuning)
        "test_ratio": 0.10,   # 45 samples (for ECE evaluation)
        "stratify_by": "difficulty",  # Balance Div1/Div2/Div3
    },

    # AST feature extraction
    "features": {
        "extractor": "radon",  # Radon v6.0.1+
        "ast_features": [
            "cyclomatic_complexity",
            "halstead_volume",
            "nesting_depth",
            "loop_count"
        ],
        "max_ast_nodes": 1000,
        "normalize": True,
    },

    # Tree-LSTM model architecture
    "model": {
        "architecture": "tree-lstm",
        "variant": "child-sum",  # Tai et al. 2015
        "hidden_dim": 256,
        "embed_dim": 128,
        "num_classes": 2,  # Pairwise: A faster vs B faster
        "dropout": 0.0,  # No dropout for EXISTENCE (add in optimization phase)
        "implementation": "dgl",  # Deep Graph Library
    },

    # Training configuration
    "training": {
        "optimizer": "adam",
        "learning_rate": 1e-3,
        "weight_decay": 1e-4,
        "batch_size": 32,
        "max_epochs": 50,
        "early_stopping": {
            "enabled": True,
            "patience": 10,
            "monitor": "val_loss",
            "min_delta": 1e-4,
        },
        "checkpoint": {
            "save_best": True,
            "save_last": False,
            "monitor": "val_loss",
        },
        "logging": {
            "log_every_n_epochs": 1,
            "progress_bar": True,
        },
    },

    # Temperature scaling calibration
    "calibration": {
        "method": "temperature_scaling",
        "temperature_bounds": [0.1, 10.0],
        "optimizer": "lbfgs",
        "max_iter": 100,
        "lr": 0.01,
        "convergence_tol": 1e-5,
        "implementation": "torch-uncertainty",  # or "gpleiss"

        # Sanity check bounds (flag if violated)
        "expected_temp_range": [0.5, 2.0],
    },

    # Evaluation metrics
    "evaluation": {
        "ece_bins": 10,
        "success_threshold": 0.05,  # ECE < 0.05 required
        "min_passing_folds": 8,      # ≥8/10 folds must pass
        "min_base_accuracy": 0.60,   # Pre-calibration accuracy

        # Diagnostic thresholds
        "max_bin_imbalance": 0.80,   # Flag if >80% in single bin
        "temp_variance_threshold": 1.0,  # Flag if σ_T > 1.0
    },

    # Visualization settings
    "visualization": {
        "output_dir": "./figures",
        "dpi": 300,
        "figsize": [8, 6],
        "reliability_diagram": {
            "show_histogram": True,
            "show_diagonal": True,
            "bin_colors": "Blues",
        },
        "save_format": "png",
    },

    # Reporting and persistence
    "reporting": {
        "results_dir": "./results",
        "save_models": True,
        "save_per_fold": True,
        "aggregate_format": "json",
        "validation_report": "04_validation.md",

        # Artifact naming
        "model_pattern": "model_fold_{fold_id}.pt",
        "results_pattern": "results_fold_{fold_id}.json",
        "plot_pattern": "reliability_fold_{fold_id}.png",
        "aggregate_file": "aggregated_results.json",
    },

    # Compute resources
    "compute": {
        "num_workers": 4,  # DataLoader workers
        "pin_memory": True,
        "parallel_folds": False,  # Set True if multiple GPUs
        "deterministic": True,    # For reproducibility

        # Resource limits
        "max_gpu_memory_gb": 8,
        "max_system_memory_gb": 16,
        "timeout_hours_per_fold": 4,
    },

    # Gate validation criteria (MUST_WORK)
    "gate": {
        "primary": {
            "metric": "ece",
            "threshold": 0.05,
            "min_passing_folds": 8,
        },
        "secondary": {
            "metric": "temperature",
            "min_value": 0.5,
            "max_value": 2.0,
        },
        "baseline": {
            "metric": "accuracy",
            "min_value": 0.60,
        },
    },
}


def get_config(mode="default"):
    """Load configuration based on execution mode."""
    import torch

    # Auto-detect device
    if not torch.cuda.is_available():
        CONFIG["experiment"]["device"] = "cpu"
        CONFIG["training"]["batch_size"] = 16  # Reduce for CPU
        CONFIG["compute"]["num_workers"] = 2
        CONFIG["compute"]["pin_memory"] = False

    return CONFIG


def validate_config(config):
    """Validate configuration constraints."""
    import torch

    device = config["experiment"]["device"]
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA device specified but not available")

    n_folds = config["experiment"]["n_folds"]
    if n_folds < 1 or n_folds > 10:
        raise ValueError(f"n_folds must be 1-10, got {n_folds}")

    t_min, t_max = config["calibration"]["temperature_bounds"]
    if t_min >= t_max or t_min <= 0:
        raise ValueError(f"Invalid temperature bounds: [{t_min}, {t_max}]")

    return True
