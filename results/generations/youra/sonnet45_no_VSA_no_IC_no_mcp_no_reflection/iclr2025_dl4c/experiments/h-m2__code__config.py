"""Configuration for H-M2 experiment."""

import os

# Get base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M1_DIR = os.path.join(os.path.dirname(BASE_DIR), "h-m1")

# Baseline: Sequential debugging
BASELINE_CONFIG = {
    # Model
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,

    # Dataset (reuse H-M1)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,

    # Debugging
    "max_iterations": 10,
    "strategy": "sequential",

    # Reproducibility
    "random_seed": 1,

    # Paths
    "h_m1_data_path": os.path.join(H_M1_DIR, "data", "problems.json"),
    "output_dir": os.path.join(BASE_DIR, "results", "baseline"),
}

# Proposed: Root cause prioritization
PROPOSED_CONFIG = {
    # Model
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,

    # Dataset (reuse H-M1)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,

    # Debugging
    "max_iterations": 10,
    "strategy": "prioritized",
    "clustering_method": "error_type",

    # Prioritizer config
    "cluster_threshold": 0.8,
    "min_cluster_size": 2,

    # Reproducibility
    "random_seed": 1,

    # Paths
    "h_m1_data_path": os.path.join(H_M1_DIR, "data", "problems.json"),
    "output_dir": os.path.join(BASE_DIR, "results", "proposed"),
}

# Evaluation
EVALUATION_CONFIG = {
    # Metric thresholds
    "high_impact_threshold": 2,

    # Success criteria
    "success_criterion": "directional",

    # Visualization
    "save_figures": True,
    "figure_dir": os.path.join(BASE_DIR, "figures"),
    "figure_formats": ["png"],
    "dpi": 300,

    # Outputs
    "results_file": os.path.join(BASE_DIR, "results", "metrics.json"),
    "fix_sequences_file": os.path.join(BASE_DIR, "results", "fix_sequences.json"),
}

# Dataset
DATASET_CONFIG = {
    # Source
    "cache_first": True,
    "h_m1_cache_path": os.path.join(H_M1_DIR, "data", "problems.json"),

    # Filtering
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,

    # Test execution
    "test_timeout": 5,
}
