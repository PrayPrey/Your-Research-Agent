"""
Configuration for H-E1 Alignment Method Clustering Analysis
LIGHT tier: Hardcoded constants for standalone execution
"""

# Environment Configuration
ENV_CONFIG = {
    "python_version": "3.9+",
    "cuda_version": "11.8+",
    "packages": [
        "evalplus",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "radon",
        "lizard",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "pandas",
        "numpy"
    ],
    "min_gpu_vram_gb": 14
}

# Data Configuration
DATA_CONFIG = {
    "dataset_name": "evalplus/humanevalplus",
    "num_problems": 164,
    "dataset_split": "test",
    "cache_dir": "./cache/datasets"
}

# Model Configuration
MODEL_CONFIG = {
    "models": [
        # Execution-focused (2 models)
        ("codellama/CodeLlama-7b-Python-hf", "execution"),
        ("bigcode/starcoder", "execution"),

        # Preference-focused (2 models)
        ("codellama/CodeLlama-7b-Instruct-hf", "preference"),
        ("meta-llama/CodeLlama-7b-hf", "preference"),

        # Baseline (2 models)
        ("codellama/CodeLlama-7b-hf", "baseline"),
        ("bigcode/starcoderbase-7b", "baseline"),
    ],
    "device_map": "auto",
    "torch_dtype": "float16",
    "trust_remote_code": True,
    "cache_dir": "./cache/models"
}

GENERATION_CONFIG = {
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "do_sample": True,
    "num_return_sequences": 1,
    "pad_token_id": 0
}

# Profiling Configuration
PROFILING_CONFIG = {
    "num_samples_per_task": 64,
    "execution_timeout_sec": 3.0,
    "num_workers": 4,
    "random_seed": 42,
    "pass_k_values": [1, 10, 100],
    "complexity_metrics": ["cyclomatic", "ast_depth"],
    "efficiency_metrics": ["runtime", "memory"],
    "profile_only_correct": True
}

# Clustering Configuration
CLUSTERING_CONFIG = {
    "standardize": True,
    "pca_components": 3,
    "k_clusters": 3,
    "kmeans_init": "k-means++",
    "kmeans_n_init": 10,
    "random_state": 42,
    "cohens_d_threshold": 1.5,
    "bootstrap_iterations": 1000
}

# Visualization Configuration
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),
    "colors": {
        "execution": "#0173B2",
        "preference": "#DE8F05",
        "baseline": "#029E73"
    },
    "figures": [
        "3d_scatter",
        "heatmap",
        "boxplots",
        "dendrogram",
        "effect_size",
        "gate_metrics"
    ]
}

# Experiment Configuration
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "checkpoint_dir": "./checkpoints",
    "log_level": "INFO",
    "process_models_sequentially": True,
    "unload_model_after_use": True,
    "save_signatures": True,
    "save_metrics": True,
    "save_raw_samples": False,
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42,
        "torch": 42
    }
}

# Gate Evaluation
GATE_CONFIG = {
    "type": "MUST_WORK",
    "metric": "cohens_d",
    "threshold": 1.5,
    "comparison": "greater_than",
    "halt_on_failure": True
}
