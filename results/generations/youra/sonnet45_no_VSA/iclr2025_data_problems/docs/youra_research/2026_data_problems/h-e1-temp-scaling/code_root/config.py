"""Configuration for H-E1: Temperature Scaling Calibration for Code Generation"""

import torch

CONFIG = {
    # Experiment metadata
    "experiment": {
        "name": "h-e1-temperature-scaling-calibration",
        "hypothesis_id": "h-e1",
        "hypothesis_type": "EXISTENCE",
        "seed": 42,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "quick_mode": False,  # Set to True for faster testing (100 samples)
    },

    # Dataset configuration (MBPP)
    "data": {
        "dataset_name": "google-research-datasets/mbpp",
        "total_problems": 974,

        # Custom splits (IDs specified in PRD)
        "splits": {
            "train": {
                "ids": list(range(601, 975)),  # 374 problems (unused in PoC)
                "size": 374,
            },
            "calibration": {
                "ids": list(range(511, 601)) + list(range(11, 121)),  # 90+110=200 problems
                "size": 200,
            },
            "validation": {
                "ids": list(range(121, 316)),  # 195 problems
                "size": 195,
            },
        },

        # Loading settings
        "cache_dir": "./data/cache",
        "num_workers": 4,
    },

    # Model configuration (Code Llama 7B)
    "model": {
        "name": "meta-llama/CodeLlama-7b-hf",
        "torch_dtype": "float16",  # Memory optimization
        "device_map": "auto",      # Automatic GPU allocation
        "trust_remote_code": True,
        "cache_dir": "./models/cache",
    },

    # Code generation settings
    "generation": {
        "temperature": 1.0,        # Uncalibrated baseline
        "max_new_tokens": 256,
        "top_p": 0.95,
        "do_sample": True,         # Sampling for diversity
        "return_dict_in_generate": True,
        "output_scores": True,     # Required for logit extraction
        "pad_token_id": 0,
    },

    # Code execution settings
    "execution": {
        "timeout": 5.0,            # Seconds per test case
        "max_workers": 8,          # Parallel execution
        "sandbox": True,           # Restricted environment
        "allowed_imports": [       # Whitelist
            "math", "itertools", "collections", "functools",
            "re", "string", "heapq", "bisect", "random"
        ],
    },

    # Temperature scaling calibration
    "calibration": {
        "method": "temperature_scaling",
        "init_temperature": 1.5,   # gpleiss default

        # LBFGS optimizer settings
        "optimizer": {
            "type": "LBFGS",
            "lr": 0.01,
            "max_iter": 200,
            "tolerance_grad": 1e-7,
            "tolerance_change": 1e-9,
            "history_size": 100,
            "line_search_fn": "strong_wolfe",
        },

        # Loss function
        "loss": "cross_entropy",   # Negative Log-Likelihood (NLL)

        # Sanity check bounds
        "expected_temp_range": [0.5, 3.0],
    },

    # ECE evaluation settings
    "evaluation": {
        "ece": {
            "task": "binary",      # Correct/incorrect
            "n_bins": 15,          # Standard ECE
            "norm": "l1",          # L1 norm = ECE (vs l2=RMSCE, max=MCE)
            "implementation": "torchmetrics",  # CalibrationError class
        },

        # Gate criteria
        "gate": {
            "metric": "ece_reduction",
            "threshold": 0.30,     # ≥30% reduction required (MUST_WORK)
            "pass_threshold": 0.30,
            "partial_threshold": 0.15,
        },

        # Secondary metrics
        "secondary_metrics": [
            "pass_at_1",           # Accuracy sanity check
            "optimal_temperature", # Learned T* value
            "nll_before",
            "nll_after",
        ],
    },

    # Visualization settings
    "visualization": {
        "output_dir": "./figures",
        "dpi": 300,
        "figsize": [10, 8],
        "format": "png",

        # Figure-specific settings
        "reliability_diagram": {
            "show_histogram": True,
            "show_diagonal": True,
            "confidence_bins": 15,
            "colors": ["#d73027", "#4575b4"],  # Before/after
        },

        "ece_comparison": {
            "bar_width": 0.6,
            "colors": ["#fc8d59", "#91bfdb"],
            "show_threshold": True,
            "threshold_color": "#2ca02c",
        },

        "calibration_curve": {
            "bins": 20,
            "alpha": 0.7,
            "colors": ["#fee090", "#abd9e9"],
        },

        "convergence_plot": {
            "show_final_value": True,
            "log_scale": False,
        },

        "per_bin_error": {
            "bar_width": 0.8,
            "colors": ["#fdae61", "#abd9e9"],
        },
    },

    # Logging and output
    "logging": {
        "level": "INFO",
        "log_dir": "./logs",
        "save_logits": False,      # Don't save large logit tensors
        "save_generations": True,  # Save generated code for debugging
        "progress_bar": True,
    },

    # Computational resources
    "compute": {
        "gpu_memory_fraction": 0.9,
        "pin_memory": True,
        "deterministic": True,     # For reproducibility
        "benchmark": False,        # Disable cuDNN auto-tuning
    },
}


def get_config():
    """Load and validate configuration."""
    config = CONFIG.copy()

    # Auto-detect CUDA availability
    if not torch.cuda.is_available():
        config["experiment"]["device"] = "cpu"
        config["model"]["device_map"] = "cpu"
        config["compute"]["pin_memory"] = False

    return config


def validate_config(config):
    """Validate configuration constraints."""
    # Check split sizes sum correctly
    cal_size = config["data"]["splits"]["calibration"]["size"]
    val_size = config["data"]["splits"]["validation"]["size"]
    assert cal_size == 200, f"Expected 200 calibration samples, got {cal_size}"
    assert val_size == 195, f"Expected 195 validation samples, got {val_size}"

    # Check temperature bounds
    t_range = config["calibration"]["expected_temp_range"]
    assert t_range[0] > 0, "Temperature must be positive"
    assert t_range[0] < t_range[1], "Invalid temperature range"

    # Check ECE bins
    n_bins = config["evaluation"]["ece"]["n_bins"]
    assert 5 <= n_bins <= 20, f"n_bins should be 5-20, got {n_bins}"

    # Check gate threshold
    gate = config["evaluation"]["gate"]["threshold"]
    assert 0 < gate < 1, f"Gate threshold must be in (0,1), got {gate}"

    return True
