INSTRUMENTATION_CONFIG = {
    "telemetry": {
        "db_path": "telemetry.db",
        "opt_in": True,
        "hash_algorithm": "sha256",
        "hash_truncate_length": 16
    },
    "benchmark": {
        "datasets": [
            ("cifar10", None),
            ("imdb", None),
            ("wikitext", "wikitext-103-v1")
        ],
        "runs_per_dataset": 10,
        "output_csv_path": "benchmark_results.csv"
    },
    "evaluation": {
        "overhead_threshold_pct": 10.0,
        "capture_rate_threshold_pct": 95.0,
        "min_event_count": 100
    },
    "simulation": {
        "event_count": 100,
        "duration_months": 6,
        "successor_adoption_rate": 0.3,
        "output_json_path": "simulation.json"
    },
    "visualization": {
        "figures_dir": "figures/",
        "dpi": 100,
        "figsize": (10, 6)
    }
}
