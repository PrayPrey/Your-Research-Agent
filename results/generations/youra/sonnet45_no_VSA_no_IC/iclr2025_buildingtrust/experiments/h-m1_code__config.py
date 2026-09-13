"""Configuration for H-M1 difficulty-controlled coupling analysis."""

CONFIG = {
    # Inherited from h-e1
    "h_e1_path": "../h-e1_code",
    "dataset": {
        "name": "thu-ml/MultiTrust",
        "samples": 500,
        "seed": 42,
        "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"]
    },

    # Difficulty generation
    "difficulty": {
        "distribution": "normal",
        "mean": 0.5,
        "std": 0.15,
        "clip_range": [0.0, 1.0],
        "seed": 42,
        "independence_threshold": 0.2
    },

    # Partial correlation analysis
    "analysis": {
        "method": "pingouin",
        "partial_phi_threshold": 0.25,
        "n_quartiles": 4,
        "min_quartile_samples": 50,
        "min_persistence_quartiles": 3
    },

    # Paths
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    },

    # Gate validation
    "gate": {
        "min_pairs_passing": 2,
        "partial_phi_threshold": 0.25,
        "quartile_persistence_threshold": 3
    }
}
