HEALTH_METRICS_CONFIG = {
    "api": {
        "hf_cache_dir": ".cache/hf",
        "pwc_cache_dir": ".cache/pwc",
        "gh_cache_dir": ".cache/gh",
        "gh_token": None,
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "backoff_base": 2,
        "timeout_seconds": 30,
    },
    "metrics": {
        "velocity_threshold": 1.0,
        "emergence_threshold": 1,
        "issue_threshold": 0.48,
        "top_k_candidates": 250,
    },
    "data": {
        "observation_months": 6,
        "download_history_days": 180,
        "dataset_sample_size": 1000,
        "output_dir": "data",
        "random_seed": 42,
    },
    "evaluation": {
        "precision_target": 0.6,
        "recall_target": 0.8,
    },
    "visualization": {
        "figures_dir": "figures",
        "dpi": 100,
        "figsize": (10, 6),
    },
    "pipeline": {
        "log_level": "INFO",
        "checkpoint_enabled": True,
        "checkpoint_dir": "checkpoints",
    },
    "testing": {
        "fixture_dir": "tests/fixtures",
        "synthetic_dataset_count": 100,
    }
}


def validate_config(config):
    assert config["api"]["rate_limit_delay"] > 0
    assert config["api"]["max_retries"] >= 0
    assert config["api"]["timeout_seconds"] > 0
    assert config["metrics"]["velocity_threshold"] > 0
    assert config["metrics"]["emergence_threshold"] > 0
    assert 0 < config["metrics"]["issue_threshold"] < 1
    assert config["metrics"]["top_k_candidates"] > 0
    assert config["data"]["observation_months"] > 0
    assert config["data"]["download_history_days"] > 0
    assert config["data"]["dataset_sample_size"] > 0
    assert 0 < config["evaluation"]["precision_target"] <= 1
    assert 0 < config["evaluation"]["recall_target"] <= 1
    return True


validate_config(HEALTH_METRICS_CONFIG)
