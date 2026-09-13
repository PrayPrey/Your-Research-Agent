"""Configuration for h-m4 CI workflow lifecycle shift experiment."""

import torch

CONFIG = {
    # Inherited from h-m3
    "validator": {
        "device_consistency": True,
        "dtype_consistency": True,
        "layout_consistency": True,
        "error_verbosity": "detailed"
    },

    # Corpus analysis
    "corpus": {
        "path": "data/jiang2023_defects.csv",
        "expected_contractable": 35,
        "filter_criteria": {
            "stage_of_failure": "environment",
            "defect_types": ["device_mismatch", "dtype_incompatibility", "layout_incompatibility"]
        }
    },

    # Trial settings
    "trial": {
        "target_repos": 42,
        "target_prs": 150,
        "seed": 42,
        "duration_weeks": 10
    },

    # GitHub API
    "api": {
        "rate_limit": 5000,
        "max_retries": 3,
        "initial_backoff": 60,
        "request_budget_per_pr": 3
    },

    # Database
    "database": {
        "path": "data/trial_data.db",
        "backup_interval": 50
    },

    # Metrics
    "metrics": {
        "ttff_reduction_threshold": 5.0,
        "detection_improvement_threshold": 25.0,
        "alpha": 0.05
    },

    # Visualization
    "visualization": {
        "output_dir": "figures/",
        "dpi": 300,
        "format": "png"
    },

    # File paths
    "paths": {
        "results": "experiment_results.json",
        "workflows": "ci_integration/workflows/"
    }
}
