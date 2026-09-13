"""
Configuration for h-e1 CCP Domain Degradation Experiment
EXISTENCE hypothesis - minimal PoC settings
"""

from pathlib import Path
import torch
import random
import numpy as np
import os

# Base paths
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

# Create directories
for d in [CACHE_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(exist_ok=True, parents=True)

# Main configuration
CONFIG = {
    "random_seed": 42,

    "dataset": {
        "truthfulqa": {
            "name": "truthfulqa/truthful_qa",
            "subset": "generation",
            "split": "validation",
            "expected_size": 817
        },
        "writingprompts": {
            "name": "euclaise/writingprompts",
            "split": "train",
            "sample_size": 817,
            "min_story_length": 200,
            "max_story_length": 2000
        },
        "cache_dir": str(CACHE_DIR / "datasets"),
        "num_proc": 4
    },

    "nli_model": {
        "name": "cross-encoder/nli-deberta-v3-base",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "batch_size": 16,
        "max_length": 512,
        "cache_dir": str(CACHE_DIR / "models")
    },

    "claim_decomposition": {
        "method": "nltk",
        "tokenizer": "punkt",
        "max_claims": 20,
        "min_claim_length": 10
    },

    "metrics": {
        "rho_j": {
            "aggregation": "median",
            "epsilon": 1e-8
        },
        "autocorrelation": {
            "max_lag": 10,
            "method": "pearson"
        },
        "reliability": {
            "sample_size": 100,
            "num_repetitions": 2
        }
    },

    "visualization": {
        "output_dir": str(FIGURES_DIR),
        "dpi": 300,
        "format": "png",
        "figsize": (10, 6),
        "colors": {
            "factual": "#1f77b4",
            "creative": "#ff7f0e"
        }
    },

    "output": {
        "intermediate": str(RESULTS_DIR / "sample_rho_j.json"),
        "metrics": str(RESULTS_DIR / "metrics_summary.json"),
        "log": str(RESULTS_DIR / "experiment.log"),
        "validation_report": str(BASE_DIR.parent / "04_validation.md")
    },

    "gate_thresholds": {
        "delta_rho_j": 0.15,
        "autocorr_creative": 0.4,
        "autocorr_factual": 0.2,
        "krippendorff_alpha": 0.7,
        "p_value": 0.05
    },

    "execution": {
        "timeout_seconds": 1800,
        "save_intermediate": True,
        "continue_on_error": True,
        "max_failures": 50
    }
}

def set_seed(seed: int = 42):
    """Configure reproducible random state across all libraries."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    # Set environment variable for determinism
    os.environ['PYTHONHASHSEED'] = str(seed)

def get_device():
    """Return available compute device."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
