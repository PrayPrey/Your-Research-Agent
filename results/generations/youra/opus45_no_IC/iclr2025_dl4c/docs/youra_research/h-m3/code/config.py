"""Configuration for H-M3 experiment: Dense Credit Assignment Convergence Efficiency."""

# Reused from H-M2
DATA_CONFIG = {
    "humaneval_dataset": "openai/openai_humaneval",
    "mbpp_dataset": "google-research-datasets/mbpp",
    "mbpp_split": "test",
    "model_name": "deepseek-ai/deepseek-coder-6.7b-instruct",
    "max_new_tokens": 256,
    "generation_temperature": 0.8,
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
    "max_length": 512,
}

TRAINING_CONFIG = {
    "algorithm": "ppo",
    "learning_rate": 1e-5,
    "lr_schedule": "cosine",
    "batch_size": 16,
    "per_device_batch": 4,
    "ppo_epochs": 4,
    "clip_epsilon": 0.2,
    "gae_lambda": 0.95,
    "gamma": 1.0,
    "max_grad_norm": 1.0,
    "weight_decay": 0.01,
}

CONVERGENCE_CONFIG = {
    "max_steps": 500,  # PoC: reduced from 5000 for faster validation
    "eval_interval": 50,  # Evaluate every 50 steps
    "target_pass1": 0.3,  # Lower target for PoC (base model ~15-25%)
    "checkpoint_every": 100,
}

EXPERIMENT_CONFIG = {
    "conditions": ["standard", "fgo"],
    "seeds": [42],  # PoC: single seed (full: [42, 123, 456])
    "output_dir": "./results",
    "checkpoint_dir": "./checkpoints",
}

GATE_THRESHOLDS = {
    "steps_to_target_ratio_max": 0.6,  # FGO steps < 60% of Standard steps
    "sample_efficiency_min_ratio": 1.5,
}

GATE_TYPE = "SHOULD_WORK"
