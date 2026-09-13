CONFIG = {
    # Model
    "model_id": "deepseek-ai/deepseek-coder-7b-base-v1.5",

    # GRPO generation
    "num_generations": 8,
    "max_new_tokens": 512,
    "temperature": 1.0,

    # Training
    "learning_rate": 1e-6,
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "max_steps": 5000,
    "save_steps": 500,
    "seed": 42,

    # Curriculum
    "curriculum_step": 2500,

    # Paths
    "output_dir": "h-e1/checkpoints",
    "log_dir": "h-e1/logs",
    "results_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",

    # Reward
    "reward_timeout": 10.0,
    "reward_epsilon": 1e-8,

    # Logging
    "reward_density_flush_interval": 100,
}

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
