"""
Configuration for h-e1: Diversity-Ranked Curriculum Scheduling
Hardcoded configuration for EXISTENCE (PoC) hypothesis validation.
"""

# Domain Diversity Scores (Pre-computed from corpus statistics)
DIVERSITY_SCORES = {
    "Pile-CC": 0.92,           # High: web text, broad vocabulary
    "StackExchange": 0.88,     # High: technical Q&A
    "Wikipedia": 0.75,         # Medium-high: encyclopedic
    "ArXiv": 0.58,             # Medium: scientific papers
    "Github": 0.42,            # Medium-low: code
    "PubMed": 0.35             # Low: biomedical papers
}

# Experimental Conditions
CONDITIONS = ["static", "diversity_ranked", "reversed", "shuffled"]

# Model Scales
MODEL_CONFIGS = {
    "1B": {
        "n_layer": 24,
        "n_head": 16,
        "n_embd": 1536,
        "n_positions": 2048,
        "vocab_size": 50257,
        "dropout": 0.1
    },
    "7B": {
        "n_layer": 32,
        "n_head": 32,
        "n_embd": 4096,
        "n_positions": 2048,
        "vocab_size": 50257,
        "dropout": 0.1
    }
}

# Training Hyperparameters
TRAINING_CONFIG = {
    "1B": {
        "lr": 3e-4,
        "betas": (0.9, 0.95),
        "weight_decay": 0.1,
        "warmup_steps": 2000,
        "total_steps": 100000,
        "batch_size": 512,
        "gradient_clip": 1.0,
        "min_lr_ratio": 0.1
    },
    "7B": {
        "lr": 1.5e-4,
        "betas": (0.9, 0.95),
        "weight_decay": 0.1,
        "warmup_steps": 2000,
        "total_steps": 150000,
        "batch_size": 1024,
        "gradient_clip": 1.0,
        "min_lr_ratio": 0.1
    }
}

# Curriculum Parameters
CURRICULUM_CONFIG = {
    "gaussian_width": 0.3,      # Width of Gaussian transition
    "min_weight": 0.05,         # Minimum 5% weight per domain
    "sequence_length": 2048,    # Tokens per sequence
    "tokens_per_domain": int(16.7e9)  # 16.7B tokens per domain
}

# Checkpoint Schedule
CHECKPOINT_PERCENTAGES = [0.10, 0.25, 0.50, 0.75, 1.0]

# Evaluation Configuration
EVAL_CONFIG = {
    "benchmarks": ["mmlu", "bigbench", "hellaswag", "winogrande"],
    "domain_specific": {
        "code": ["humaneval", "mbpp"],
        "scientific": ["scienceqa"]
    },
    "eval_frequency": 1000,  # Evaluate every N steps
    "n_shot": 5
}

# Seeds for Reproducibility
SEEDS = [42, 43, 44, 45, 46]

# Experiment Matrix: 4 conditions × 2 scales × 5 seeds = 40 runs
EXPERIMENT_MATRIX = []
for condition in CONDITIONS:
    for scale in ["1B", "7B"]:
        for seed in SEEDS:
            EXPERIMENT_MATRIX.append({
                "condition": condition,
                "scale": scale,
                "seed": seed
            })

# Statistical Testing
STATISTICAL_CONFIG = {
    "alpha": 0.05,
    "bonferroni_n": 4,  # 4 pairwise comparisons
    "min_effect_size": {
        "1B": 0.02,  # 2.0% absolute improvement
        "7B": 0.005  # 0.5% absolute improvement
    }
}
