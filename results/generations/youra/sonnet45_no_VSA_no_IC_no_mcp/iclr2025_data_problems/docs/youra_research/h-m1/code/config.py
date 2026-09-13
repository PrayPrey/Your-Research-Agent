"""
Configuration for h-m1 Threshold Transfer Experiment
PoC tier - fixed threshold ranges from 03_config.md
"""
from pathlib import Path

# Threshold sweep (DataComp pattern)
THRESHOLD_CONFIG = {
    "dedup_thresholds": [0.7, 0.8, 0.9],
    "perplexity_thresholds": [500, 1000, 1500],
}

# Training (from h-e1)
TRAINING_CONFIG = {
    "optimizer": "adamw",
    "learning_rate": 2e-5,
    "weight_decay": 0.01,
    "betas": (0.9, 0.999),
    "batch_size": 16,
    "micro_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "epochs": 3,
    "seed": 1,
    "deterministic": True,
}

# Datasets
DATASET_CONFIG = {
    "pretrain": {
        "name": "allenai/c4",
        "split": "train",
        "streaming": True,
        "num_samples": 52002,
    },
    "finetune": {
        "name": "databricks/databricks-dolly-15k",
        "split": "train",
        "num_samples": 15000,
    },
    "max_length": 512,
    "min_words": 5,
    "cache_dir": "~/.cache/huggingface/",
    "curated_data_dir": "data/h-m1/curated",
}

# Model
MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-2-7b-hf",
    "tokenizer_name": "meta-llama/Llama-2-7b-hf",
    "full_finetuning": True,
    "gradient_checkpointing": False,
    "bf16": True,
    "fp16": False,
    "checkpoint_dir": "data/h-m1/checkpoints",
}

# Evaluation
EVALUATION_CONFIG = {
    "tasks": ["mmlu", "hellaswag"],
    "num_fewshot": 0,
    "eval_batch_size": 8,
    "gate_type": "MUST_WORK",
    "max_delta": 0.10,  # 10% threshold
    "mock_evaluation": True,
}

# Visualization
VISUALIZATION_CONFIG = {
    "figures_dir": "docs/youra_research/h-m1/figures",
    "format": "png",
    "dpi": 300,
    "required_figures": [
        "gate_metrics_comparison.png",
        "threshold_sensitivity_heatmap.png",
        "transfer_delta_barchart.png",
        "curation_impact_chart.png",
    ],
}

# Paths - use absolute from script location
_SCRIPT_DIR = Path(__file__).parent.parent.resolve()

PATH_CONFIG = {
    "hypothesis_dir": _SCRIPT_DIR,
    "data_dir": _SCRIPT_DIR / "data",
    "cache_dir": Path.home() / ".cache" / "huggingface",
    "curated_data_dir": _SCRIPT_DIR / "data" / "curated",
    "output_dir": _SCRIPT_DIR / "results",
    "checkpoint_dir": _SCRIPT_DIR / "data" / "checkpoints",
    "figures_dir": _SCRIPT_DIR / "figures",
    "log_file": _SCRIPT_DIR / "experiment.log",
}

# Master config
CONFIG = {
    "hypothesis_id": "h-m1",
    "experiment_name": "threshold_transfer_robustness",
    "tier": "PoC",
    "thresholds": THRESHOLD_CONFIG,
    "training": TRAINING_CONFIG,
    "dataset": DATASET_CONFIG,
    "model": MODEL_CONFIG,
    "evaluation": EVALUATION_CONFIG,
    "visualization": VISUALIZATION_CONFIG,
    "paths": PATH_CONFIG,
}
