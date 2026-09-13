"""
Experiment Configuration
Based on: 03_config.md - All configuration sections
"""

# Global Configuration
DEFAULT_CONFIG = {
    # Model
    "model_name": "meta-llama/Llama-2-7b-hf",
    "torch_dtype": "float16",

    # LoRA adapters
    "lora_ranks": [4, 8, 16, 32],
    "lora_alpha": 16,
    "lora_dropout": 0.1,
    "target_modules": ["q_proj", "v_proj"],

    # Training
    "learning_rate": 3e-4,
    "min_lr": 1e-6,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.999,
    "adam_epsilon": 1e-8,
    "warmup_ratio": 0.1,

    # Batch and accumulation
    "batch_size": 16,
    "gradient_accumulation_steps": 2,
    "max_seq_length": 512,

    # Epochs (task-dependent)
    "epochs_small": 5,      # <10k samples
    "epochs_large": 3,      # >50k samples
    "early_stopping_patience": 2,

    # Loss
    "label_smoothing": 0.1,

    # Reproducibility
    "seed": 42,

    # Datasets
    "glue_tasks": ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli"],
    "xtreme_languages": ["en", "es", "de", "zh"],

    # Paths
    "output_dir": "./outputs",
    "cache_dir": "./cache",

    # Device
    "device": "cuda",
    "fp16": True,

    # Gradient settings
    "max_grad_norm": 1.0,
}


# Task-specific configurations
TASK_CONFIGS = {
    # GLUE tasks
    "cola": {
        "num_labels": 2,
        "metric": "matthews_correlation",
        "epochs": 5,
    },
    "sst2": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "mrpc": {
        "num_labels": 2,
        "metric": "f1",
        "epochs": 5,
    },
    "qqp": {
        "num_labels": 2,
        "metric": "f1",
        "epochs": 3,
    },
    "stsb": {
        "num_labels": 1,  # Regression
        "metric": "pearson",
        "epochs": 5,
        "loss": "mse",
    },
    "mnli": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "qnli": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "rte": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 5,
    },
    "wnli": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 5,
    },

    # XTREME tasks (XNLI)
    "xnli_en": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_es": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_de": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_zh": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },

    # XTREME tasks (PAWS-X)
    "pawsx_en": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_es": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_de": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_zh": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
}


# Evaluation Configuration
EVAL_CONFIG = {
    # Oracle gap calculation
    "hypervolume_ref_point": [0.0, 1e12],

    # Per-task oracle selection
    "oracle_selection_metric": "accuracy",

    # Fixed-rank baselines
    "fixed_ranks": [4, 8, 16, 32],

    # Success criteria
    "target_oracle_gap": 0.10,  # 10% normalized gap

    # Metrics to track
    "metrics": [
        "accuracy",
        "flops",
        "params",
        "hypervolume",
    ],
}


def get_task_config(task_name):
    """Get task-specific configuration."""
    return TASK_CONFIGS.get(task_name, {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    })
