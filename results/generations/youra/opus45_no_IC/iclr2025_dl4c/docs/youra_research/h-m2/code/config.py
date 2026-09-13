"""Configuration for H-M2 experiment: Token Masking Gradient Exclusion."""

DATA_CONFIG = {
    "humaneval_dataset": "openai/openai_humaneval",
    "mbpp_dataset": "google-research-datasets/mbpp",
    "mbpp_split": "test",
    "total_problems": 664,
    "model_name": "meta-llama/CodeLlama-7b-Instruct-hf",
    "max_new_tokens": 256,
    "generation_temperature": 0.8,
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
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
    "training_steps": 1000,
    "episodes": 100,
    "max_grad_norm": 1.0,
    "weight_decay": 0.01,
    "checkpoint_every": 50,
}

MASKING_CONFIG = {
    "conditions": ["none", "random", "trace"],
    "zero_grad_eps": 1e-8,
    "match_sparsity_to_trace": True,
}

EVAL_CONFIG = {
    "k": 1,
    "num_samples": 1,
    "significance_test": "paired_ttest",
    "alpha": 0.05,
}

PIPELINE_CONFIG = {
    "seeds": [42, 123, 456],
    "trace_timeout_sec": 5.0,
    "overhead_bench_samples": 100,
    "output_dir": "./outputs",
    "log_every": 20,
}

GATE_THRESHOLDS = {
    "trace_vs_random_p": 0.05,
    "gradient_exclusion": True,
}

# Gate type for H-M2
GATE_TYPE = "MUST_WORK"
