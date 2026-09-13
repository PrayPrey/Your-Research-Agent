"""
Configuration for H-M4: Cross-Architecture Directional Replication
Multi-model family evaluation (5 families × 5 seeds)
"""

# Model families for cross-architecture testing
MODEL_FAMILIES = {
    "llama": {
        "model_id": "meta-llama/Llama-3.2-1B",
        "architecture": "transformer",
        "size": "1B",
        "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]
    },
    "mistral": {
        "model_id": "mistralai/Mistral-7B-v0.1",
        "architecture": "transformer-gqa",
        "size": "7B",
        "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]
    },
    "qwen": {
        "model_id": "Qwen/Qwen-1.8B",
        "architecture": "transformer",
        "size": "1.8B",
        "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "c_proj"]
    },
    "mamba": {
        "model_id": "state-spaces/mamba-1.4b",
        "architecture": "ssm",
        "size": "1.4B",
        "lora_target_modules": ["in_proj", "out_proj"]  # SSM-specific
    },
    "falcon": {
        "model_id": "tiiuae/falcon-7b",
        "architecture": "transformer",
        "size": "7B",
        "lora_target_modules": ["query_key_value", "dense"]
    }
}

# LoRA configuration (from h-m3 optimal settings)
LORA_CONFIG = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.1,
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# Training configuration
TRAINING_CONFIG = {
    "num_seeds": 5,  # Increased from h-m3's 3 for statistical power
    "num_epochs": 3,
    "learning_rate": 2e-4,
    "batch_size": 8,
    "gradient_accumulation_steps": 4,
    "max_samples": 500,
    "optimizer": "adamw",
    "weight_decay": 0.01,
    "warmup_steps": 50
}

# Evaluation dimensions (same as h-m3)
DIMENSIONS = ["truthfulness", "fairness", "robustness"]

# Directional classification thresholds
DIRECTION_THRESHOLDS = {
    "positive": 0.3,   # r > 0.3
    "negative": -0.3,  # r < -0.3
    # neutral: -0.3 <= r <= 0.3
}

# Gate criterion
GATE_CRITERION = {
    "type": "SHOULD_WORK",
    "replication_threshold": 0.6,  # ≥3/5 models = 60%
    "min_models_required": 3
}

# Datasets (from h-m3)
DATASETS = {
    "truthfulness": {
        "name": "truthful_qa",
        "config": "generation",
        "split": "validation",
        "metric": "mc1_accuracy"
    },
    "fairness": {
        "name": "HiTZ/bbq",
        "split": "test",
        "metric": "accuracy"
    },
    "robustness": {
        "name": "anli",
        "split": "test_r3",
        "metric": "accuracy"
    }
}

# Output paths
OUTPUT_DIR = "outputs"
FIGURES_DIR = "../figures"
RESULTS_FILE = "results.csv"
EXPERIMENT_RESULTS_FILE = "../experiment_results.json"
