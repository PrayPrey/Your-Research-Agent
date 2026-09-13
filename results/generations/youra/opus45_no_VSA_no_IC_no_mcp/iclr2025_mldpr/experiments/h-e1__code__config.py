"""Fixed configuration for h-e1 DNSI computation experiment."""

CONFIG = {
    "seed": 1,
    "window_months": 6,
    "min_sota_entries": 15,  # ponytail: reduced from 50 for PoC with synthetic data
    "min_history_years": 3,
    "dnsi_valid_range": (0.0, 2.0),
    "success_rate_threshold": 0.5,
    "data_dir": "data/pwc",
    "figures_dir": "figures",
    "pwc_repo_url": "https://github.com/paperswithcode/paperswithcode-data",
}

TARGET_BENCHMARKS = {
    "ImageNet": 1000,
    "CIFAR-10": 10,
    "CIFAR-100": 100,
    "MNIST": 10,
    "GLUE": None,
    "SQuAD": None,
    "WMT En-De": None,
    "COCO Detection": 80,
}
