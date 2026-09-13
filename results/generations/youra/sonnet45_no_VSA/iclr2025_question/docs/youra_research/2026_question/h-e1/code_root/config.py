"""Configuration for h-e1: KLE vs SE comparison experiment."""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
for dir_path in [DATA_DIR, CACHE_DIR, RESULTS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

CONFIG = {
    # Reproducibility
    "random_seed": 42,

    # Dataset Configuration
    "dataset": {
        "name": "trivia_qa",
        "hf_path": "trivia_qa",
        "subset": "rc.wikipedia",
        "validation_size": 1000,  # PoC: reduced
        "test_size": 500,  # PoC: reduced
        "cache_dir": os.path.join(DATA_DIR, "triviaqa"),
    },

    # Model Configuration
    "models": {
        "qa_model": {
            "name": "meta-llama/Llama-2-7b-chat-hf",
            "cache_dir": os.path.join(CACHE_DIR, "llama2"),
            "device": "cuda:0",
            "dtype": "float16",
        },
        "embedding_model": {
            "name": "microsoft/deberta-v2-xlarge-mnli",
            "cache_dir": os.path.join(CACHE_DIR, "deberta"),
            "device": "cuda:0",
            "embedding_dim": 1024,
            "batch_size": 32,
        },
    },

    # Sampling Configuration
    "sampling": {
        "n_samples": 20,
        "temperature": 1.0,
        "top_p": 0.95,
        "max_tokens": 50,
        "batch_size": 4,
        "do_sample": True,
    },

    # Stratification Configuration
    "stratification": {
        "window": 0.1,
        "tercile_percentiles": [33.33, 66.67],
        "epsilon_oracle": 0.6,
    },

    # Uncertainty Configuration
    "uncertainty": {
        "se": {
            "method": "hard_clustering",
            "epsilon_grid": [0.5, 0.55, 0.6, 0.65, 0.7],
        },
        "kle": {
            "method": "gaussian_kernel",
            "sigma_oracle": 0.3,
            "sigma_grid": [0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
        },
    },

    # Evaluation Configuration
    "evaluation": {
        "n_permutations": 10000,
        "significance_alpha": 0.05,
        "bonferroni_correction": True,
        "seeds": [42],  # PoC: single seed
    },

    # Synthetic Validation Configuration (deferred in PoC)
    "synthetic": {
        "n_questions": 100,
        "n_paraphrases": 5,
        "paraphrase_model": "gpt-4",
        "temperature": 0.7,
    },

    # Hardware Configuration
    "hardware": {
        "gpu_memory_gb": 40,
        "cpu_cores": 16,
        "storage_gb": 100,
    },

    # Cache Configuration
    "cache": {
        "answers_dir": os.path.join(CACHE_DIR, "answers"),
        "embeddings_dir": os.path.join(CACHE_DIR, "embeddings"),
        "enable_caching": True,
        "checksum_validation": True,
    },

    # Logging Configuration
    "logging": {
        "level": "INFO",
        "format": "json",
        "output_dir": LOGS_DIR,
    },

    # Success Gates
    "gates": {
        "oracle_pre_gate_threshold": 0.03,
        "synthetic_bd_ratio_threshold": 0.5,
        "primary_auroc_threshold": 0.02,
        "spearman_rho_threshold": 0.5,
        "reproducibility_std_threshold": 0.01,
    },
}
