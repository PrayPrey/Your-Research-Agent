"""Configuration for H-M2 width-scaling experiment."""

import sys
from pathlib import Path

# Add h-e1 to Python path for imports
h_e1_path = Path(__file__).parent.parent.parent / "docs" / "youra_research" / "h-e1" / "code"
sys.path.insert(0, str(h_e1_path))

try:
    from config import CONFIG as H_E1_CONFIG
except ImportError:
    # Fallback if h-e1 config not available
    H_E1_CONFIG = {
        "modelzoo_path": "./h-m2/data/modelzoo_cifar10/",
        "sample_size": 1000,
        "random_seed": 42,
    }

CONFIG = {
    **H_E1_CONFIG,

    # Override modelzoo path for h-m2 (use absolute path)
    "modelzoo_path": str(Path(__file__).parent.parent / "data" / "modelzoo_cifar10"),

    # Width-Scaling Parameters
    "hidden_widths": [8, 16, 32, 64, 128],
    "model_types": ["mlp", "nfn"],

    # Training
    "optimizer": "adam",
    "lr": 1e-3,
    "weight_decay": 1e-5,
    "batch_size": 64,
    "epochs": 50,

    # Loss Matching
    "loss_match_tolerance": 0.01,

    # NFN Architecture
    "nfn_num_layers": 4,
    "nfn_input_channels": 1,

    # MLP Architecture (will be auto-detected from data)
    "mlp_input_dim": None,  # Auto-detected
    "mlp_hidden_dims": [512, 256],

    # Data splits
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,

    # Output Paths (use absolute paths)
    "checkpoint_dir": str(Path(__file__).parent.parent / "checkpoints"),
    "results_dir": str(Path(__file__).parent.parent / "results"),
    "figures_dir": str(Path(__file__).parent.parent / "figures"),
}
