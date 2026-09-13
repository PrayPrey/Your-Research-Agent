"""Configuration for H-E1 coupling analysis experiment."""

CONFIG = {
    "models": {
        "gpt-4": {
            "model": "gpt-4",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        },
        "claude-3-sonnet": {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        },
        "llama-3-70b": {
            "model": "meta-llama/Llama-3-70b",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        }
    },
    "dataset": {
        "name": "thu-ml/MultiTrust",
        "samples": 500,
        "seed": 42,
        "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"]
    },
    "statistical": {
        "phi_threshold": 0.3,
        "p_threshold": 0.01
    },
    "api": {
        "batch_size": 10,
        "retry_max": 3,
        "retry_delay": 5
    },
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
