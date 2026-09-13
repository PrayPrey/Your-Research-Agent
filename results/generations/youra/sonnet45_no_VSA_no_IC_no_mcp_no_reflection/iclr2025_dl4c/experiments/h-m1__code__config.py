# h-m1 Experiment Configuration

EXPERIMENT_CONFIG = {
    # Model
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout": 60,

    # Dataset
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,

    # Debugging loop
    "max_iterations": 10,
    "test_timeout": 5,

    # Annotation
    "min_annotators": 2,
    "kappa_threshold": 0.7,
    "error_types": ["syntax", "runtime", "logic", "edge_case"],

    # Metrics
    "clustering_threshold": 0.3,
    "p_value_threshold": 0.05,
    "num_permutations": 1000,

    # Reproducibility
    "random_seed": 1,

    # API
    "codeforces_rate_limit": 10,
    "openai_retry_count": 3,
    "retry_backoff": 2.0,

    # Paths
    "output_dir": "docs/youra_research/h-m1/results",
    "figures_dir": "docs/youra_research/h-m1/figures",
    "cache_dir": "docs/youra_research/h-m1/cache",
    "annotations_path": "docs/youra_research/h-m1/data/annotations.json",
}


def validate_config(config: dict) -> None:
    """Validate experiment configuration."""
    assert config["model"].startswith("gpt-4"), "Must use GPT-4"
    assert 0 <= config["temperature"] <= 1, "Temperature in [0, 1]"
    assert config["num_problems"] >= 50, "Need 50+ problems"
    assert config["min_test_cases"] >= 15, "Need 15+ test cases"
    assert config["kappa_threshold"] >= 0.7, "Kappa must be ≥ 0.7"
    assert config["clustering_threshold"] == 0.3, "Gate threshold fixed"
    assert config["p_value_threshold"] == 0.05, "Gate threshold fixed"
    assert config["random_seed"] == 1, "Reproducibility: seed=1"
